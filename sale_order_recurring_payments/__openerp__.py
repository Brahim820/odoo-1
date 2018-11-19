# -*- coding: utf-8 -*-
{
    'name': "Sale Order Recurring Payments",

    'summary': """
        Compute due payments on recurring contracts using sale orders.""",

    'author': "Fábrica de Software Libre",
    'website': "www.libre.ec",

    'category': 'Event',
    'version': '9.0.0.0.1',

    'depends': ['base', 'sale'],

    # always loaded
    'data': [
        'views/sale_order.xml',
        'views/product.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],

    'installable': True,
    'auto_install': False,
}
