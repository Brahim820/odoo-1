# -*- coding: utf-8 -*-
{
    'name': "SRI - Comercio Exterior",
    'summary': """Add international commerce features.""",
    'version': '9.0.1.0.0',
    'author': "Fabrica de Software Libre,Odoo Community Association (OCA)",
    'maintainer': 'Fabrica de Software Libre',
    'website': 'http://www.libre.ec',
    'license': 'AGPL-3',
    'category': 'Account',
    'depends': [
        'base',
        'l10n_ec_sri',
    ],
    'data': [
        'views/account_fiscal_position.xml',
        'views/res_partner.xml',
        'data/account.fiscal.position.csv',
        'data/account.fiscal.position.map_account.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
}
