# -*- coding: utf-8 -*-
{
    'name': "Keyboard support in Point Of Sale",
    'author': "Serpent Consulting Services Pvt. Ltd.",
    'summary': 'Module allows to use usual keyboard (not virtual one) in Point of Sale',
    "website": "http://www.serpentcs.com",
    'images': ['images/keyboard.png'],
    'category': 'Point Of Sale',
    'depends': ['point_of_sale'],
    'qweb': ['static/src/xml/pos_keyboard.xml'],
    'data': [
        'data.xml',
        'views/product_inherit.xml'
    ],
    'installable': True,
    'auto_install': False,
}
