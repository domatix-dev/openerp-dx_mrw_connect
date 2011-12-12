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

class mrw_iapi(osv.osv):
    
    _name = "mrw.iapi"
    _description = "MRW IAPI object"

    _columns = {
                'lines':fields.one2many('mrw.iapi.line', 'iapi_id', 'Lines'),
                'name':fields.char('Nombre', size=128),
                'partner_code':fields.char('Nombre', size=128),
                'campaign_code':fields.char('Nombre', size=128),
                'shop_id': fields.many2one('sale.shop', 'Shop'),
                'file': fields.binary('Archivo'),
    }
    
    def _check_shop(self, cr, uid, ids):
        iapi = self.browse(cr, uid, ids[0])
        if iapi.shop_id:
                return True
        return False
    def _check_partner_code(self, cr, uid, ids):
        iapi = self.browse(cr, uid, ids[0])
        if iapi.shop_id.mrw_partner_code:
                return True
        return False
    def _check_campaign_code(self, cr, uid, ids):
        iapi = self.browse(cr, uid, ids[0])
        if iapi.shop_id.mrw_campaign_code:
                return True
        return False
    def _check_iapi_path(self, cr, uid, ids):
        iapi = self.browse(cr, uid, ids[0])
        if iapi.shop_id.iapi_path:
                return True
        return False
    
    _constraints = [
        (_check_shop, 'You can not create IAPI from purchase without shop.', ['shop_id']),
        (_check_iapi_path, 'You can not create IAPI from purchase with shop without IAPI path.', ['shop_id']),
        (_check_partner_code, 'You can not create IAPI from purchase with shop without partner code.', ['shop_id']),
        (_check_campaign_code, 'You can not create IAPI from purchase with shop without campaign code.', ['shop_id']),
    ]
    def generate_file(self, cr, uid, ids, context=None):
        iapi_line_pool = self.pool.get('mrw.iapi.line')
        for iapi_id in ids:
            output = ''
            for iapi_line_id in iapi_line_pool.search(cr, uid, [('iapi_id', '=', iapi_id)]) :
                output += iapi_line_pool.generate_txt(cr, uid, iapi_line_id)
            self.write(cr, uid, iapi_id, {'file':output})
            text = output
            iapi = self.read(cr, uid, [iapi_id], ['name'])[0]
            filename  = iapi['name'] + '.txt'
            outputFile = open( "/home/roberto/"+ filename, "w" ) 
            outputFile.write(output.encode("iso-8859-1")) 
            outputFile.close()
        return True
        
mrw_iapi()  

class mrw_api_line(osv.osv):
    
    _name = "mrw.iapi.line"
    _description = "MRW IAPI line object"
    
    _columns = {
                'name':fields.char('Nombre', size=128),
                'tipo_reg': fields.char('Tipo Registro', size=1, required=True),
                'tipo_dem': fields.char('Tipo Demanda', size=1, required=True),
                'demanda': fields.char('Demanda', size=20, required=True),
                'albaran': fields.char('Codigo Albaran', size=20),
                'cliente': fields.char('Codigo Cliente', size=20, required=True),
                'fecha_s': fields.char('Fecha recepcion', size=8, required=True),
                'fecha_d': fields.char('Fecha Documento', size=8, required=True),
                'prioridad': fields.char('Prioridad', size=1),
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
                'movil2': fields.char('Movil de facturacion de origen o destino', size=20),
                'provincia2': fields.char('Provincia de facturacion de origen o destino', size=20),
                'pais2': fields.char('Pais de facturacion de origen o destino', size=20),
                'nif2': fields.char('NIF de facturacion de origen o destino', size=9),
                'ean2': fields.char('Codigo EAN13 de facturacion de origen o destino', size=13),
                'tratamiento': fields.char('Tipo de tratamiento', size=20),
                'peso': fields.float('Peso'),#, size=12),
                'volumen': fields.float('Volumen'),#, size=13),
                'bultos': fields.integer('Bultos'),#, size=9),
                'depto': fields.char('Departamento del cliente', size=20),
                'observacion': fields.char('Observaciones libres', size=30),
                'iapi_id': fields.many2one('mrw.iapi','IAPI', required=True),
                'num_l': fields.char('Numero de linea del cliente', size=20, required=True),
                'articulo_id': fields.char('Codigo del articulo', size=20, required=True),
                'cantidad_d': fields.integer('Cantidad del articulo', required=True),#, size=9),
                'lote': fields.char('Lote', size=20),
                'gama': fields.char('Gama', size=20),
                'fecha_c': fields.char('Fecha de caducidad', size=8),
                'tratamiento_l': fields.char('Tipo de tratamiento', size=20),
                'contenedor': fields.char('Numero o matricula del contenedor', size=20),
                'num_l_prov': fields.char('Numero de linea de la demanda del proveedor', size=20),
    }
    
    _defaults = {
                'tipo_reg': 'H',
                'tipo_dem': 'P',
                'blancos': '                   ',
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
                ['movil2', 20],
                ['provincia2', 20],
                ['pais2', 20],
                ['nif2', 9],
                ['ean2', 13],
                ['tratamiento', 20],
                ['peso', 8,3],
                ['volumen', 6,6],
                ['bultos', 9,0],
                ['depto', 20],
                ['observacion', 30],
                ['num_l', 20],
                ['articulo_id', 20],
                ['cantidad_d', 9,0],
                ['lote', 20],
                ['gama', 20],
                ['fecha_c', 8],
                ['tratamiento_l', 20],
                ['contenedor', 20],
                ['num_l_prov', 20],
    ]

    # fill a variable with blank spaces to fit the desired size
    def fill_with_char(self, var, desired_size, char = ' ', char_position = 'right'):
        if var == False:
            var = ''
        var = str(var)
        if len(var) < desired_size:
            actual_size = len(var)
            for i in range(actual_size, desired_size):
                if char_position == 'right':
                    var += char
                else:
                    var = char + var
        return var
    
    def generate_txt(self, cr, uid, id):
        #load line object
        linea = self.browse(cr, uid, id)
        #default output
        output = ''
        #complete every field to fit exactly specification chars
        for size in self._sizes:
            field_name = size[0]
            field_size = size[1]
            # if field has no decimal part will be processed as text (extra positions will be spaces)
            if len(size) == 2: 
                string = self.fill_with_char(linea[field_name], field_size, ' ', 'right')
            # if field has decimal part will be processed as number (zeroes added instead of spaces)
            elif len(size) == 3:
                field_decimals = size[2]
                number = linea[field_name]
                int_part = int(number)
                # add 0 to left part of the number
                string = self.fill_with_char(linea[field_name], field_size, '0', 'left')
                if field_decimals != 0 :
                    # convert decimals to integer
                    dec_part = int ((number - int(number)) * (10 ** field_decimals)) 
                    # insert decimal separator to string
                    string += '.' 
                    # add 0 to the right part of the decimal part
                    string += self.fill_with_char(dec_part, size[2], '0', 'right')
            output += string        
        return output
    
mrw_api_line()