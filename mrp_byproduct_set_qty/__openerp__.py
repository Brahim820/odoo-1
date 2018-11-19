# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'MRP Byproducts set qty',
    'version': '1.0',
    'category': 'Manufacturing',
    'description': """
This module allows you to define the qty on subproducts.
========================================================

    """,
    'website': 'www.fslibre.com',
    'depends': ['base', 'mrp', 'mrp_byproduct'],
    'data': [
        'wizards/mrp_product_produce_view.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
