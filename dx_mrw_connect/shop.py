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
import os
import time
from datetime import datetime
import netsvc

class sale_shop(osv.osv):
    _inherit = "sale.shop"
    
    
    _columns = {
        'iapi_path': fields.char('IAPI Path', size=128),
        'iapo_path': fields.char('IAPO Path', size=128),
        'iapo_processed': fields.datetime('IAPO last processed'),
        'iapo_auto': fields.boolean('IAPO auto process'),
        'mrw_partner_code': fields.char('MRW Partner Code', size=64),
        'mrw_campaign_code': fields.char('MRW Campaign Code', size=64),
        }
 
    _defaults = {
                 'iapo_auto': False,
                 }
    
    def run_iapo_processing(self, cr, uid, ids=False):
        
        iapo_obj = self.pool.get('mrw.iapo')
        wf_service = netsvc.LocalService("workflow")
        shop_ids = self.search(cr,uid,[('iapo_auto','=',True)])
        for shop in self.browse(cr,uid,shop_ids):
            now = datetime.now().strftime("'%Y-%m-%d %H:%M:%S'")
            last = shop.iapo_processed
            now = time.strftime('%Y-%m-%d %H:%M:%S')
            iapo_path = shop.iapo_path
            if iapo_path[-1] <> '/':
                iapo_path += '/'    
            for filename in os.listdir(iapo_path) :
                file_time = datetime.fromtimestamp(os.path.getmtime(iapo_path+filename)).strftime('%Y-%m-%d %H:%M:%S')
                if file_time > last:
                    #TODO: crearlo con el fichero
                    values = {'name':filename,
                              'created':now,
                              'shop_id':shop.id}
                    iapo_id = iapo_obj.create(cr,uid,values)
                    #TODO: ejecutar workflow
                    wf_service.trg_validate(uid, 'mrw.iapo', iapo_id, 'iapo_set_checking', cr)           
            self.write(cr,uid,shop.id,{'iapo_processed':now})
            
                
        return True
    
sale_shop()