# -*- coding: utf-8 -*-
{
    'name': 'POS Price List',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 0,
    'author': 'TL Technology',
    'website': 'http://bruce-nguyen.com',
    'price': '50',
    'description': """
        Support POS Price List \n
        Price will updating when change the quantity of line \n
        Price will updatting when you change customer \n
    """,
    "currency": 'EUR',
    'depends': ['point_of_sale', 'sale'],
    'data': [
        '__import__/template.xml',
        'view/pos_config.xml',
        'view/pos_order.xml',
        'view/pricelist.xml',
        'view/res_partner.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'application': True,
    'images': ['static/description/icon.png'],
    'license': 'LGPL-3',
    'support': 'thanhchatvn@gmail.com'
}
