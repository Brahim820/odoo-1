# -*- coding: utf-8 -*-
{
    'name': "Ecuador's Tax Account Mapping",
    'summary': """Map taxes and it's account in NIIF BASE.""",
    'version': '9.0.1.0.0',
    'author': "Fabrica de Software Libre,Odoo Community Association (OCA)",
    'maintainer': 'Fabrica de Software Libre',
    'website': 'http://www.libre.ec',
    'license': 'AGPL-3',
    'category': 'Account',
    'depends': [
        'base',
        'account',
        'l10n_ec_sri',
    ],
    'data': [
        "data/l10n_ec_sri.101_map_account.xml",
        "data/l10n_ec_sri.103_map_account.xml",
        "data/l10n_ec_sri.104_map_account.xml",
        "data/account.fiscal.position.map_account.xml",
    ],
    'demo': [],
    'test': [],
    'installable': True,
}
