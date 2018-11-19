# -*- coding: utf-8 -*-

{
    'name': 'POS kitchen',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 6,
    'author': 'Webveer',
    'summary': 'Easy way to organise your kitchen orders',
    'description': """

=======================
Easy way to organise your kitchen orders
""",
    'depends': ['pos_sync_order'],
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
    'price': 90,
    'currency': 'EUR',
}
