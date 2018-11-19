# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright © 2016 Techspawn Solutions. (<http://techspawn.in>).
# 
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': "POS restrictions",

    'summary': """
         Pos Restriction on Users.""",

    'author': "Fábrica de Software Libre",

    'category': 'Point of sale',
    'version': '9.0.0.0.1',

    'depends': ['base', 'point_of_sale'],

    'data': [
        'views/point_of_sale.xml',
        'views/users.xml',
        'security/security.xml', 
    ],
}