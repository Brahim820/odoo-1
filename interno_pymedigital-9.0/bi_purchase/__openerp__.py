# -*- coding: utf-8 -*-
{
    'name': "BI Account",
    'version': '9.0.0.1.',
    'author': "Fabrica de software libre",
    'website': "www.fslibre.com",
    'depends': [
        'account',
        'bi_base',
    ],
    'data': [
        'reports/bi_account_report_view.xml',
    ],
    'external_dependencies': {
        'python': ['openpyxl']
    },
    'qweb': [
    ],
    'installable': True,
}
