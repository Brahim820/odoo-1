# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Sale Discount Amount',
    'version': '9.0.1.0.0',
    'category': 'Sales Management',
    'author': 'Heraclito, '
              'Fábrica de Software Libre, '
              'Odoo Community Association (OCA)',
    'website': 'https://odoo-community.org',
    'license': 'AGPL-3',
    'summary': 'Compute of total discount on sale order',
    'depends': [
        'sale',
    ],
    'data': [
        'views/sale_order_view.xml',
    ],
    'installable': True,
}
