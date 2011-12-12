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

class product_product(osv.osv):
    _inherit = "product.product"
    
    
    def _mrw_code(self, cursor, user, ids, name, args, context=None):
        res = {}
        for product in self.browse(cursor, user, ids, context=context):
            res[product.id] = product.default_code
        return res
    
    _columns = {
        'mrw_code': fields.function(_mrw_code, method=True, string='MRW Code'),
        }
 
    
product_product()