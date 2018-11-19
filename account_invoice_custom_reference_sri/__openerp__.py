# -*- coding: utf-8 -*-
{
    'name': "Invoice custom reference, adding the Sequence",
    'summary': """Users can use their own Invoice custom reference,
    adding the sequence to it.""",
    'version': '9.0.1.0.1',
    'author': "Fabrica de Software Libre",
    'maintainer': 'Fabrica de Software Libre',
    'website': 'http://www.fslibre.com',
    'license': 'AGPL-3',
    'category': 'Account',
    'depends': [
        'account',
        'account_invoice_custom_reference',
        'l10n_ec_sri',
    ],
    'data': [
        #'data/account_move_line_data.xml'
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
