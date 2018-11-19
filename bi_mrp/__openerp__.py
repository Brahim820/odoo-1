# -*- coding: utf-8 -*-
{
    'name': "BI for Mrp",
    'version': '9.0.1.0.',
    'author': "Fabrica de software libre",
    'website': "www.libre.ec",
    'depends': [
        'mrp',
        'stock_available_unreserved',
    ],
    'data': [
        'wizards/bi_mrp_report_wizard.xml', #1
    ],
    'external_dependencies': {
        'python': ['openpyxl']
    },

    'qweb': [
    ],
    'installable': True,
}
