# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015  ADHOC SA  (http://www.adhoc.com.ar)
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
    'name': 'Base federate',
    'version': '9.0.0.0.0',
    'category': 'Tools',
    'sequence': 14,
    'author': 'FÁBRICA DE SOFTWARE LIBRE',
    'website': 'www.libre.ec',
    'license': 'AGPL-3',
    'images': [
    ],
    'depends': [
        'base',
    ],
    'external_dependencies': {
        'python': ['odoorpc']
    },
    'data': [
        'views/res_partner.xml',
        'views/federate.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}