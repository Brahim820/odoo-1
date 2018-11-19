# -*- coding: utf-8 -*-

{
    'name': 'POS Multi Receipt',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 6,
    'author': 'Webveer',
    'summary': 'This module allows you to print one receipt N times',
    'description': """

=======================

This module allows you to print one receipt N times.

""",
    'depends': ['point_of_sale'],
    'data': [
        'views/views.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    'images': [
        'static/description/receipt.jpg',
    ],
    'installable': True,
    'website': '',
    'auto_install': False,
    'price': 20,
    'currency': 'EUR',
}
