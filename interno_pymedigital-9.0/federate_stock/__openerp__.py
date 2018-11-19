# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Fábrica de Software Libre: info@fslibre.com
#    All Rights Reserved.
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
    'name': 'Federation for stock',
    'version': '9.0.0.0.1',
    'category': 'stock',
    'sequence': 14,
    'author': 'FÁBRICA DE SOFTWARE LIBRE',
    'website': 'www.libre.ec',
    'license': 'AGPL-3',
    'images': [
    ],
    'depends': [
        'base',
        'stock',
        'base_federate',
    ],
    'data': [
        'views/stock.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
