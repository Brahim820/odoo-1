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


{
    'name': 'Default Customer in POS',
    'version': '1.0',
    'category': 'POS',
    'description': """
    """,
    'author': 'Opencloud',
    'summary': 'Default Customer in POS',
    'license': 'LGPL-3',
    'website': 'http://opencloud.pro',
    'depends': ["point_of_sale"],
    'init_xml': [],
    'data': [
        'templates.xml',
        "inherits_view.xml",
        ],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['images/imagem_default_customer_pos.png'],
    'price': 29.00,
    'currency': 'EUR',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
