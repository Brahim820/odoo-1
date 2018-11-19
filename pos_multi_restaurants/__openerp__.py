# -*- coding: utf-8 -*-

{
    'name': 'POS Multiple Restaurants',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 6,
    'author': 'Webveer',
    'summary': "Manage Multiple Restaurants With a single POS and Easy way to manage Floors." ,
    'description': """

=======================

Manage Multiple Restaurants With a single POS and Easy way to manage Floors.

""",
    'depends': ['pos_restaurant'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml'
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    'images': [
        'static/description/main.png',
    ],
    'installable': True,
    'website': '',
    'auto_install': False,
    'price': 60,
    'currency': 'EUR',
}
