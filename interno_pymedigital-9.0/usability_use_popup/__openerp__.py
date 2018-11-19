# -*- coding: utf-8 -*-
{
    'name': "Popup on models",
    'summary': """Changes editable tree to popup in some models.""",
    'version': '9.0.1.0.0',
    'author': "Fabrica de Software Libre,Odoo Community Association (OCA)",
    'maintainer': 'Fabrica de Software Libre',
    'website': 'http://www.libre.ec',
    'license': 'AGPL-3',
    'category': 'Account',
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'views/account_invoice.xml',
        'views/account_move.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
}
