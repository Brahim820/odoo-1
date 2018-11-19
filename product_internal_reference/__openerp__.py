# -*- coding: utf-8 -*-
{
    'name': "Product Internal Reference ",

    'summary': """ Agrega campo referencia interna de producto en vista lista""",

    'author': "Fábrica de Software Libre",
    'website': "www.libre.ec",

    'category': 'Event',
    'version': '9.0.0.0.2',

    'depends': ['product'],

    # always loaded
    'data': [
        'views/product_view.xml',
    ],
    'qweb': [],
    # only loaded in demonstration mode
    'demo': [
    ],

    'installable': True,
    'auto_install': False,
}
