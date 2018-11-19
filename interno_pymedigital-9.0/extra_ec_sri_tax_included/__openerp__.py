# -*- coding: utf-8 -*-
{
    'name': "Ecuador's Tax Included",
    'summary': """Agrega impuestos incluídos.""",
    'version': '9.0.1.0.0',
    'author': "Fabrica de Software Libre,Odoo Community Association (OCA)",
    'maintainer': 'Fabrica de Software Libre',
    'website': 'http://www.libre.ec',
    'license': 'AGPL-3',
    'category': 'Account',
    'depends': [
        'l10n_ec_sri',
    ],
    'data': [
        "data/sri/104/account.tax.csv",
    ],
    'demo': [],
    'test': [],
    'installable': True,
}
