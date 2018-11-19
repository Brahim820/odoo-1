# -*- coding: utf-8 -*-
{
    'name': "Restaurante- Impresión local",
    'summary': 'Permite la impresión de Ordenes de manera local',
    'description': """

=======================

Permite la impresión de Ordenes de manera local

        """,
    'author': "",
    'website': "",
    'category': 'Point of Sale',
    'version': '9.0.1.0.0',
    'depends': ['pos_restaurant'],
    'data': [
        'views/pos_restaurant_print_local_templates.xml',
        'views/point_of_sale.xml',
    ],
    'qweb': [
        'static/src/xml/print_local.xml',
    ],
    'installable': True,
    # 'website': '',
    'auto_install': False,
}