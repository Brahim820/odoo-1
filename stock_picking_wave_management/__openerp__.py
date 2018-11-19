# -*- coding: utf-8 -*-
{
    'name':
    "Advanced wave picking management.",
    'version':
    '9.0.1.0.',
    'author':
    "Fabrica de software libre",
    'website':
    "www.libre.ec",
    'depends': [
        'stock', 'mrp', 'purchase', 'procurement', 'stock_picking_wave',
        'mrp_mto_with_stock'
    ],
    'data': [
        'wizards/wave_report_wizard.xml',  # 1
        'views/stock.xml',  # 2
        'security/ir.model.access.csv',
        'security/security.xml',
    ],
    'external_dependencies': {
        'python': ['openpyxl']
    },
    'qweb': [],
    'installable':
    True,
}
