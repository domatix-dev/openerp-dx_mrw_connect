# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010 Domatix Technologies  S.L. (http://www.domatix.com) 
#                       info <info@domatix.com>
#                        Angel Moya <angel.moya@domatix.com>
#
#        $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################
from osv import osv, fields
import time
from datetime import datetime

class purchase_order(osv.osv):
    _inherit = "purchase.order"
    
    _columns = {
        'iapi_id': fields.many2one('mrw.iapi', 'IAPI'),
        'shop_id': fields.many2one('sale.shop', 'Shop'),
       }
    
    
    def generate_iapi(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        # objetos
        iapi_pool = self.pool.get('mrw.iapi')
        iapi_line_pool = self.pool.get('mrw.iapi.line')
        
        for purchase in self.browse(cr,uid,ids,context):
            # Creo el iapi
            iapi_vals = {}
            name = False
            codigo_cliente = False
            codigo_campanya = False
            if purchase.shop_id:
                codigo_cliente = purchase.shop_id.mrw_partner_code 
                codigo_campanya = purchase.shop_id.mrw_partner_code
                if codigo_cliente and codigo_campanya:
                    name = 'IAPI_'+codigo_cliente+'_'+codigo_campanya+'_'+time.strftime('%Y%m%d%H%M%S') 
            iapi_vals = {'name':name,
                         'shop_id':purchase.shop_id.id,
                             }
            
            iapi_id = iapi_pool.create(cr,uid,iapi_vals, context)
        
            # Creo las lineas asociadas al iapi
            for line in purchase.order_line:
                
                line_vals = {
                            'demanda': purchase.name,
                            'fecha_s': time.strftime('%d%m%Y', time.strptime(purchase.minimum_planned_date[:10],'%Y-%m-%d')),
                            'fecha_d': time.strftime('%d%m%Y', time.strptime(purchase.date_approve[:10], '%Y-%m-%d')),
                            'od': purchase.partner_id.name,
                            'iapi_id':iapi_id, 
                            'num_l': 0, # En pedidos de compra no hay número de lineas
                            'articulo_id': line.product_id.mrw_code,
                            'cantidad_d': line.product_qty
                            }
                iapi_line_id = iapi_line_pool.create(cr,uid,line_vals, context)
        
            # Genero el fichero
            
            iapi_pool.generate_file(cr,uid,[iapi_id])
        
            self.write(cr, uid, sale.id, {'iapi_id':iapi_id})
        
        return True

    
purchase_order()