# -*- coding: utf-8 -*-
{
    'name': "Sale Order invoice line management",

    'summary': """
        Manage invoice lines related to a sale order line.""",

    'author': "Fábrica de Software Libre",
    'website': "www.fslibre.com",

    'category': 'Sale',
    'version': '9.0.0.0.1',

    'depends': [
        'base',
        'sale',
        'account',
    ],

    'data': [
        'views/sale_order.xml',
    ],
    'demo': [
    ],

    'installable': True,
    'auto_install': False,
}
