# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'POS Payment colors',
    'version': '9.0.0.0.1',
    'category': 'Point of Sale',
    'summary': 'Change colors on pos payment',
    'depends': [
        'point_of_sale',
        'account',
    ],
    'data': [
        'views/account_account.xml',
        'views/templates.xml',
    ],
    'demo': [
    ],
    'qweb': [
        'static/src/xml/pos_payment_colors.xml',
    ],
    'installable': True,
    'auto_install': False,
}
