# -*- coding: utf-8 -*-
{
    'name': "Stock location kardex",
    'version': '9.0.0.1.',
    'author': "Fabrica de software libre",
    'website': "www.fslibre.com",
    'depends': [
        'stock',
    ],
    'data': [
        'security/security.xml',
        'views/stock.xml',
        'security/ir.model.access.csv',
        'reports/report_stock_kardex.xml',
    ],
    'external_dependencies': {
        'python': ['openpyxl']
    },
    'qweb': [
    ],
    'installable': True,
}
