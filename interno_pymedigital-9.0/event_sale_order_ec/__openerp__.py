# -*- coding: utf-8 -*-
{
    'name': "Event Sale Order for Ecuador",

    'summary': """
        Event sale order for Ecuador.""",

    'author': "Fábrica de Software Libre",
    'website': "www.libre.ec",

    'category': 'Event',
    'version': '9.0.0.0.1',

    'depends': ['event_sale_order', 'l10n_ec_sri'],

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
