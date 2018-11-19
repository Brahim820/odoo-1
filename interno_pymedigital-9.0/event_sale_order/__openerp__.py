# -*- coding: utf-8 -*-
{
    'name': "Event Sale Order",

    'summary': """
        Use sale orders to register montly payments in long term events.""",

    'author': "Fábrica de Software Libre",
    'website': "www.libre.ec",

    'category': 'Event',
    'version': '9.0.0.2.1',

    'depends': [
        'base',
        'event',
        'sale',
        'sale_service',
        'event_sale',
        'sale_order_recurring_payments',
        'l10n_ec_sri_sale',
        ],

    # always loaded
    'data': [
        'views/event.xml',
        'views/sale_order.xml',
        'views/account_invoice.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],

    'installable': True,
    'auto_install': False,
}
