# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv, orm
import time, datetime
import netsvc

class mrw_iapo(osv.osv):
    
    _name = "mrw.iapo"
    _description = "MRW IAPO Processing"

    _columns = {
                'lines':fields.one2many('mrw.iapo.line', 'iapo_id', 'Lines'),
                'messages':fields.one2many('mrw.iapo.message', 'iapo_id', 'Messages'),
                'name':fields.char('Nombre', size=128),
                #'file': fields.binary('Archivo', required=True),
                'created': fields.datetime('Date created', readonly=True),
                'shop_id': fields.many2one('sale.shop', 'Shop'),
                'user_id': fields.many2one('res.users', 'Created by', readonly=True, select=True),
                'state': fields.selection([
                    ('draft', 'Draft'),
                    ('checking', 'Checking'),
                    ('processed', 'Processed'),
                    ('error', 'Error'),
                    ('cancel', 'Cancel')],
                    'State', readonly=True,
                    help='When the MRW IAPO Processing is created the state is \'Draft\'.\n It is processed by the user, the state is \'Processed\'.\n If an error ocurs, the state is \'Error\'.\n User can cancel it, the state is \'Cancel\'.'
                ),
                'description': fields.text('Description'),
    }
    
    _defaults = {
        'state':'draft',
        'created': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': lambda obj, cr, uid, context: uid,
        }
    

    
    def create(self, cr, uid, vals, context=None):
        iapo_id = super(mrw_iapo, self).create(cr, uid, vals, context=context)
        if 'name' in vals :
            self.pool.get('mrw.iapo.line').file_to_object(cr, uid, iapo_id, vals['name'], vals['shop_id'])
        return iapo_id
    
    def iapo_processing(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        iapo_msg_obj = self.pool.get('mrw.iapo.message')
        iapo_line_obj = self.pool.get('mrw.iapo.line')
        partner_obj = self.pool.get('res.partner')
        purchase_obj = self.pool.get('purchase.order')
        product_obj = self.pool.get('product.product')
        purchase_line_obj = self.pool.get('purchase.order.line')
        stock_move_obj = self.pool.get('stock.move')
        for id in ids:
            line_ids = iapo_line_obj.search(cr,uid,[('iapo_id','=',id)])
            for line in iapo_line_obj.browse(cr,uid,line_ids):
                    partner_ids = partner_obj.search(cr,uid,[('name','=',line.od)])
                    if not partner_ids:
                        msg = 'Error - Proveedor ['+line.od+'] de la linea ['+line.num_l+'] del IAPO no existe en OpenERP' #TODO: recuperar el error, pueden ser varios por linea
                        iapo_msg_obj.create(cr,uid,{'iapo_id':line.iapo_id.id,'name':msg})
                        self.iapo_cancel(cr, uid, ids)
                        return True
                    partner_id = partner_ids[0]
                    
                    purchase_ids = purchase_obj.search(cr,uid,[('name','=',line.demanda),('partner_id','=',partner_id)])
                    if not purchase_ids:
                        msg = 'Error - Pedido de compra ['+line.demanda+'] del proveedor ['+line.od+'] de la linea ['+line.num_l+'] del IAPO no existe en OpenERP' #TODO: recuperar el error, pueden ser varios por linea
                        iapo_msg_obj.create(cr,uid,{'iapo_id':line.iapo_id.id,'name':msg})
                        self.iapo_cancel(cr, uid, ids)
                        return True
                    purchase_id = purchase_ids[0]
                        
                    product_ids = product_obj.search(cr,uid,[('mrw_code','=',line.articulo_id)]) # esto cambia para magento
                    if not product_ids:
                        msg = 'Error - Producto ['+line.articulo_id+'] de la linea ['+line.num_l+'] del IAPO no existe en OpenERP' #TODO: recuperar el error, pueden ser varios por linea
                        iapo_msg_obj.create(cr,uid,{'iapo_id':line.iapo_id.id,'name':msg})
                        self.iapo_cancel(cr, uid, ids)
                        return True
                    product_id = product_ids[0]
                    
                    purchase_line_ids = purchase_line_obj.search(cr,uid,[('order_id','=',purchase_id),('product_id','=',product_id),('product_qty','=',line.cantidad_original)])
                    if not purchase_line_ids:
                        msg = 'Error - Linea del pedido de cantidad ['+line.cantidad_original+'] del producto ['+line.articulo_id+'] de la linea ['+line.num_l+'] del IAPO no existe en OpenERP' #TODO: recuperar el error, pueden ser varios por linea
                        iapo_msg_obj.create(cr,uid,{'iapo_id':line.iapo_id.id,'name':msg})
                        self.iapo_cancel(cr, uid, ids)
                        return True
                    purchase_line_id = purchase_line_ids[0]
                    
                    #TODO:  Comprobar entregas parciales, con los movimientos generados por el pedido de compra.
                    #       Consultar como se realizan las entregas parciales. 
                    stock_move_ids = stock_move_obj.search(cr,uid,[('purchase_line_id','=',purchase_line_id),('state','=','assigned')])
                    if not stock_move_ids:
                        msg = 'Error - Movimiento de la linea ['+line.num_l+'] del pedido de compra ['+line.demanda+']del IAPO no existe en OpenERP' 
                        iapo_msg_obj.create(cr,uid,{'iapo_id':line.iapo_id.id,'name':msg})
                        self.iapo_cancel(cr, uid, ids)
                        return True
                    stock_move_id = stock_move_ids[0]
                    
                    stock_move = stock_move_obj.browse(cr,uid,stock_move_id)
                    # Hay varios casos con los movimientos, si estan creados:
                    # - Entrega total, de entrada ya creada
                    if stock_move and stock_move.product_qty == line.cantidad_original and stock_move.product_qty == line.cantidad_d :
                        stock_move_obj.action_done(cr,uid,[stock_move_id]) 
                        msg = 'Validado Movimiento - Movimiento de la linea ['+line.num_l+'] del pedido de compra ['+line.demanda+']del IAPO validado en OpenERP, movimiento ['+stock_move.name+']' 
                        iapo_msg_obj.create(cr,uid,{'iapo_id':line.iapo_id.id,'name':msg})
                        
                    # - Entrega parcial, de entrada ya creada
                    elif stock_move and stock_move.product_qty == line.cantidad_original and line.cantidad_original != line.cantidad_d :
                        #TODO: Crear linea del resto
                        stock_move_obj.write(cr,uid,stock_move_id,{'product_qty':line.cantidad_d})
                        stock_move_obj.action_done(cr,uid,stock_move_id) 
                        msg = 'Validado Movimiento Parcial- Movimiento de la linea ['+line.num_l+'] del pedido de compra ['+line.demanda+']del IAPO validado en OpenERP, movimiento ['+stock_move.name+'] entregado ['+line.cantidad_d+'] de ['+line.cantidad_original+']' 
                        iapo_msg_obj.create(cr,uid,{'iapo_id':line.iapo_id.id,'name':msg})
                    else:
                        msg = 'No se ha encontrado movimiento compatible' 
                        iapo_msg_obj.create(cr,uid,{'iapo_id':line.iapo_id.id,'name':msg})
                        self.iapo_cancel(cr, uid, ids)
                        return True

                
        # Si todo ha ido bien
        self.iapo_processed(cr, uid, ids)
            
        return True
        
    def iapo_draft(self, cr, uid, ids):
        iapo_msg_obj = self.pool.get('mrw.iapo.message')
        for id in ids:
            msg = 'Creado'
            iapo_msg_obj.create(cr,uid,{'iapo_id':id,'name':msg})
        self.write(cr, uid, ids, { 'state': 'draft' })
        return True
    
    def iapo_checking(self, cr, uid, ids):
        self.write(cr, uid, ids, { 'state': 'checking' })
        self.iapo_processing(cr, uid, ids)
        return True
       
    def iapo_processed(self, cr, uid, ids):
        iapo_msg_obj = self.pool.get('mrw.iapo.message')
        for id in ids:
            msg = 'Procesado'
            iapo_msg_obj.create(cr,uid,{'iapo_id':id,'name':msg})
        self.write(cr, uid, ids, { 'state': 'processed' })
        return True
     
    def iapo_cancel(self, cr, uid, ids):
        iapo_msg_obj = self.pool.get('mrw.iapo.message')
        for id in ids:
            msg = 'Cancelado'
            iapo_msg_obj.create(cr,uid,{'iapo_id':id,'name':msg})
        self.write(cr, uid, ids, { 'state': 'cancel' })
        return True
    
    def iapo_error(self, cr, uid, ids):
        # El mensaje de error habrá que crearlo en otro sitio
        self.write(cr, uid, ids, { 'state': 'error' })
        return True
        
   
mrw_iapo()  

class mrw_iapo_message(osv.osv):
    
    _name = "mrw.iapo.message"
    _description = "MRW IAPO message"
    
    _columns = {
                'name':fields.text('Nombre'),
                'created': fields.datetime('Date Created', readonly=True),
                'iapo_id': fields.many2one('mrw.iapo', 'MRW IAPO'),}
    
    _defaults = {
        'created': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        }
mrw_iapo_message()

class mrw_apo_line(osv.osv):
    
    _name = "mrw.iapo.line"
    _description = "MRW IAPO line object"
    
    _columns = {
                'name':fields.char('Nombre', size=128),
                'iapo_id': fields.many2one('mrw.iapo', 'MRW IAPO'),
                'tipo_reg': fields.char('Tipo Registro', size=1, required=True),
                'tipo_dem': fields.char('Tipo Demanda', size=1, required=True),
                'demanda': fields.char('Demanda', size=20, required=True),
                'albaran': fields.char('Codigo Albaran', size=20),
                'cliente': fields.char('Codigo Cliente', size=20, required=True),
                'fecha_s': fields.char('Fecha recepcion', size=8, required=True),
                'fecha_d': fields.char('Fecha Documento', size=8, required=True),
                'prioridad': fields.char('Prioridad', size=1, required=True),
                'blancos': fields.char('Blancos', size=19, required=True),
                'p_carga': fields.char('Codigo proveedor', size=20),
                'p_servicio': fields.char('Codigo origen en entrega', size=20),
                'dispositivo': fields.char('Dispositivo organizativo', size=20),
                'transportista': fields.char('Codigo de transportista', size=20),
                'od': fields.char('Codigo origen, destino, proveedor...', size=20, required=True),
                'nombre': fields.char('Nombre de origen o destino', size=50),
                'direccion': fields.char('Direccion de origen o destino', size=100),
                'poblacion': fields.char('Poblacion de origen o destino', size=50),
                'cod_postal': fields.char('Codigo postal de origen o destino', size=20),
                'telefono': fields.char('Telefono de origen o destino', size=20),
                'movil': fields.char('Movil de origen o destino', size=20),
                'provincia': fields.char('Provincia de origen o destino', size=20),
                'pais': fields.char('Pais de origen o destino', size=20),
                'nif': fields.char('NIF de origen o destino', size=9),
                'ean': fields.char('Codigo EAN13 de origen o destino', size=13),
                'od2': fields.char('Codigo de facturacion origen o destino', size=20),
                'nombre2': fields.char('Nombre de facturacion de origen o destino', size=50),
                'direccion2': fields.char('Direccion de facturacion de origen o destino', size=100),
                'poblacion2': fields.char('Poblacion de facturacion de origen o destino', size=50),
                'cod_postal2': fields.char('Codigo postal de facturacion de origen o destino', size=20),
                'telefono2': fields.char('Telefono de facturacion de origen o destino', size=20),
                'provincia2': fields.char('Provincia de facturacion de origen o destino', size=20),
                'pais2': fields.char('Pais de facturacion de origen o destino', size=20),
                'nif2': fields.char('NIF de facturacion de origen o destino', size=9),
                'ean2': fields.char('Codigo EAN13 de facturacion de origen o destino', size=13),
                'tratamiento': fields.char('Tipo de tratamiento', size=20),
                'peso': fields.float('Peso'),#, digits(8,3)),#, size=12),
                'volumen': fields.float('Volumen'),#, digits(6,6)),#, size=13),
                'bultos': fields.integer('Bultos'),#, size=9),
                'depto': fields.char('Departamento del cliente', size=20),
                'observacion': fields.char('Observaciones libres', size=30),
                'num_l': fields.char('Numero de linea del cliente', size=20, required=True),
                'articulo_id': fields.char('Codigo del articulo', size=20, required=True),
                'cantidad_d': fields.integer('Cantidad del articulo', required=True),#, size=9),
                'lote': fields.char('Lote', size=20),
                'gama': fields.char('Gama', size=20),
                'fecha_c': fields.char('Fecha de caducidad', size=8),
                'estado_ds': fields.char('Estado de disponibilidad del articulo', size=20),
                'estado_qc': fields.char('Estado de calidad del articulo', size=20),
                'tratamiento_l': fields.char('Tipo de tratamiento', size=20),
                'contenedor': fields.char('Numero o matricula del contenedor', size=20),
                'num_l_prov': fields.char('Numero de linea de la demanda del proveedor', size=20),
                'observacion_l': fields.char('Observaciones libres linea', size=30),
                'incidencia': fields.char('Codigo de la excepcion o incidencia', size=20),
                'cantidad_original': fields.integer('Cantidad original del articulo', required=True),
                }
    
    """
    Array to store field sizes. Format: ['field_name', field_size, field_decimals]
    WARNING: Only set decimals for numeric fields! (will be filled with zeroes in IAPI creation
        string field example: 'test string' => ['example_field', 15] => will output 'test_string    '
        int field example: 34  => ['example_int', 4, 0] => will output: '0034'
        float field example: 2.5 => ['example_float', 13, 6] => will output: '000002.500000'
    
    To fill integer field with spaces instead of zeroes declare it as string. Example:
        34 => ['example_int', 4] => will output '34  '
    FIELDS MUST BE DECLARED FOLLOWING EXACTLY THE IAPO ORDER
    """
    _sizes = [
                ['tipo_reg', 1],
                ['tipo_dem', 1],
                ['demanda', 20],
                ['albaran', 20],
                ['cliente', 20],
                ['fecha_s', 8],
                ['fecha_d', 8],
                ['prioridad', 1],
                ['blancos', 19],
                ['p_carga', 20],
                ['p_servicio', 20],
                ['dispositivo', 20],
                ['transportista', 20],
                ['od', 20],
                ['nombre', 50],
                ['direccion', 100],
                ['poblacion', 50],
                ['cod_postal', 20],
                ['telefono', 20],
                ['movil', 20],
                ['provincia', 20],
                ['pais', 20],
                ['nif', 9],
                ['ean', 13],
                ['od2', 20],
                ['nombre2', 50],
                ['direccion2', 100],
                ['poblacion2', 50],
                ['cod_postal2', 20],
                ['telefono2', 20],
                ['provincia2', 20],
                ['pais2', 20],
                ['nif2', 9],
                ['ean2', 13],
                ['tratamiento', 20],
                ['peso', 12, 3],
                ['volumen', 13, 6],
                ['bultos', 9,0],
                ['depto', 20],
                ['observacion', 30],
                ['num_l', 20],
                ['articulo_id', 20],
                ['cantidad_d', 9,0],
                ['lote', 20],
                ['gama', 20],
                ['fecha_c', 8],
                ['estado_ds', 20],
                ['estado_qc', 20],
                ['tratamiento_l', 20],
                ['contenedor', 20],
                ['num_l_prov', 20],
                ['observacion_l', 30],
                ['incidencia', 20],
                ['cantidad_original', 9,0]
              ]
    
    def file_to_object(self, cr, uid, iapo_id, filename, shop_id,context=None):
        
        shop_obj = self.pool.get('sale.shop')
        message_obj = self.pool.get('mrw.iapo.message')
        shop = shop_obj.browse(cr,uid,shop_id)
        iapo_path = shop.iapo_path
        if iapo_path[-1] <> '/':
            iapo_path += '/'
        file_path = iapo_path + filename
        
        try:
            file = open(file_path,"r")
            fin = False
            while not fin:
                vals={}
                for size in self._sizes:
                    field_name = size[0]
                    field_size = size[1]
                        
                    value = file.read(field_size)          # read by character
                    if not value:
                        fin = True 
                        break
                    
                    if len(size) == 3: # es float y hay que cambiar , por .
                        value = value.replace(',','.')
                        
                    vals[field_name]=value.strip()
                if vals <> {}:
                    salto_linea = file.read(1)
                    vals['iapo_id'] = iapo_id
                    iapo_line_id = self.create(cr,uid,vals)
            
            file.close()
        
        except Exception, e:
            
            mesagge_vals={'name':'ERROR Importando el fichero '+file_path+', no se ha podido leer el fichero o no cumple las especificaciones',
                          'iapo_id':iapo_id}
            message_id = message_obj.create(cr,uid,mesagge_vals)
            
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'mrw.iapo', iapo_id, 'iapo_set_error', cr)
            
            #raise orm.except_orm(_('Unknown Error'), str(e))
        return True    
mrw_apo_line()