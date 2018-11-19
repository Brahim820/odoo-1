# -*- coding: utf-8 -*-
{
    'name': "Bank statement import",
    'summary': """Permite importar los pagos para la conciliación bancaria.""",
    'version': '9.0.1.0.0',
    'author': "Jonathan Finlay <jfinlay@riseup.net>",
    'maintainer': 'Jonathan Finlay <jfinlay@riseup.net>',
    'website': 'http://www.lalibre.net',
    'license': 'AGPL-3',
    'category': 'account',
    'depends': [
        'account',
    ],
    'data': [
        'views/account_bank_statement_view.xml',
        'reports/report_bank_statement.xml'
    ],
    'demo': [],
    'test': [],
    'installable': True,
}
