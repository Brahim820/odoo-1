# -*- coding: utf-8 -*-
{
    'name': "Sale Order invoice lines for Ecuador",

    'summary': """
        Add ecuador specific fields to sale order invoice lines detail.""",

    'author': "Fábrica de Software Libre",
    'website': "www.libre.ec",

    'category': 'Event',
    'version': '9.0.0.0.1',

    'depends': ['sale_order_invoice_lines', 'l10n_ec_sri'],

    # always loaded
    'data': [
        'views/sale_order.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],

    'installable': True,
    'auto_install': False,
}
