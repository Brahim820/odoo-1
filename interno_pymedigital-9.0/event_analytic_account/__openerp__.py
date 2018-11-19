# -*- coding: utf-8 -*-
{
    'name': "Event Analytic Account",

    'summary': """
        Analytic Accounts for events on sale orders.""",

    'author': "Fábrica de Software Libre",
    'website': "www.libre.ec",

    'category': 'Event',
    'version': '9.0.0.0.1',

    'depends': ['base','event', 'sale', 'analytic', 'event_sale', 'event_sale_order', ],

    # always loaded
    'data': [
        'views/sale_order.xml',
        'views/event.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],

    'installable': True,
    'auto_install': False,
}
