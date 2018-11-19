# -*- coding: utf-8 -*-
{
    'name': "Ecuador Local Payments",
    'summary': """Add local payments and check printing for Ecuador.""",
    'version': '9.0.1.0.0',
    'author': "Fabrica de Software Libre,Odoo Community Association (OCA)",
    'maintainer': 'Fabrica de Software Libre',
    'website': 'http://www.libre.ec',
    'license': 'AGPL-3',
    'category': 'Account',
    'depends': [
        'base',
        'account_check_printing',
        'payment',
    ],
    'data': [
        'data/account_payment_method.xml',
        'views/account_payment.xml',
        'views/account_invoice.xml',
        'views/res_bank.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'test': [],
    'installable': True,
}
