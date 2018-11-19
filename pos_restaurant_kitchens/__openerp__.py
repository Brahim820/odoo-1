    # -*- coding: utf-8 -*-

{
    'name': 'POS Restaurant Kitchens',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 6,
    'author': 'Webveer',
    'summary': 'Easy way to organize your kitchen, floors, tables and Guests.',
    'description': """

=======================
Easy way to organize your kitchen, floors, tables and Guests.
""",
    'depends': ['pos_sync_restaurant','pos_kitchen'],
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
        # 'views/templates.xml'
    ],
    'qweb': [
        # 'static/src/xml/pos.xml',
    ],
    'images': [
        'static/description/print.jpg',
    ],
    'installable': True,
    'website': '',
    'auto_install': False,
    'price': 20,
    'currency': 'EUR',
}
