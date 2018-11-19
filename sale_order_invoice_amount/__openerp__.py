# -*- coding: utf-8 -*-
{
    'name': "Sale order easy invoice",

    'summary': """
        New method to invoice fast on sale orders.""",

    'author': "Fábrica de Software Libre",
    'website': "www.libre.ec",

    'category': 'Event',
    'version': '9.0.0.0.2',

    'depends': ['base', 'sale', 'l10n_ec_sri'],

    # always loaded
    'data': [
        'views/sale_order.xml',
        'wizard/sale_make_invoice_advance.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],

    'installable': True,
    'auto_install': False,
}
