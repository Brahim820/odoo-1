# -*- coding: utf-8 -*-
{
    'name': "Invoice custom reference",
    'summary': """Users can use their own Invoice custom reference.""",
    'version': '9.0.1.0.1',
    'author': "Fabrica de Software Libre",
    'maintainer': 'Fabrica de Software Libre',
    'website': 'http://www.fslibre.com',
    'license': 'AGPL-3',
    'category': 'Account',
    'depends': [
        'base',
        'l10n_ec_sri',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_invoice.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
