
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010 Domatix Technologies S.L (http://www.domatix.com) All Rights Reserved.
#                        info <info@domatix.com>
#                        Ángel Moya <angel.moya@domatix.com>
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

{
    "name": "MRW Connect",
    "version": "0.1",
    "author" : "Domatix",
    "website" : "http://www.domatix.com",
    "category": "Generic Modules/Others",
    "description": """
        Generación e importacion de ficheros de intercambio de MRW.
        Extensión para utilizar el codigo de productos de magento en los IAPI. 
    """,
    "license" : "GPL-3",
    "depends": ['dx_mrw_connect','magentoerpconnect'],
    "init_xml": [],
    'update_xml': [
        "purchase_view.xml",
        ],
    'demo_xml': [],
    'installable': True,
    'active': False,
#    'certificate': 'certificate',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
