# -*- coding: utf-8 -*-

{
    'name': 'POS Restaurant Sync',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 6,
    'author': 'Webveer',
    'summary': 'Easy way to Sync Restaurant orders',
    'description': """

=======================
Easy way to Sync Restaurant orders
""",
    'depends': ['pos_sync_order','pos_restaurant'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml'
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    'images': [
        'static/description/kitchen.jpg',
    ],
    'installable': True,
    'website': '',
    'auto_install': False,
    'price': 80,
    'currency': 'EUR',
}
