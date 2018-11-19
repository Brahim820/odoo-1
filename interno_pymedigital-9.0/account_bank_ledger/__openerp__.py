# -*- coding: utf-8 -*-
{
    'name' : 'Bank General Ledger',
    'version' : '1.1',
    'summary': 'Print bank ledger',
    'author': "Jonathan Finlay <jfinlay@riseup.net>",
    'maintainer': 'Jonathan Finlay <jfinlay@riseup.net>',
    'website': 'http://www.lalibre.net',
    'sequence': 30,
    'description': """
Bank Ledger
===========
Print Bank ledger
    """,
    'category' : 'Accounting & Finance',
    'website': 'http://www.lalibre.net',
    'depends' : ['account', 'l10n_ec_sri'],
    'data': [
        'wizard/account_report_bank_ledger_view.xml',
        'views/report_bankledger.xml',
        'views/report.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
