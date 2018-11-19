# -*- coding: utf-8 -*-
{
    'name': "Payments compensation",
    'summary': """Allow to compensate payables and receivables from a partner.""",
    'version': '9.0.1.0.0',
    'author': "Fabrica de Software Libre,Odoo Community Association (OCA)",
    'maintainer': 'Fabrica de Software Libre',
    'website': 'http://www.libre.ec',
    'license': 'AGPL-3',
    'category': 'Account',
    'depends': [
        'base',
        'payment',
    ],
    'data': [
        'data/account_payment_method.xml',
        'views/account_payment.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
}
