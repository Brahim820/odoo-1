# -*- coding: utf-8 -*-
{
    'name': "Recibos de compra y venta - Ecuador",
    'summary': """Recibos de compra y venta.""",
    'version': '9.0.1.0.0',
    'author': "Jonathan Finlay <jfinlay@riseup.net>",
    'maintainer': 'Jonathan Finlay <jfinlay@riseup.net>',
    'website': 'http://www.lalibre.net',
    'license': 'AGPL-3',
    'category': 'Account',
    'depends': [
        'base',
        'account_voucher',
    ],
    'data': [
        'views/account_voucher_view.xml'
    ],
    'demo': [],
    'test': [],
    'installable': True,
}
