# -*- coding: utf-8 -*-
{
    'name': "Stock picking template discrepancy",
    'version': '9.0.1.0.',
    'author': "Fabrica de software libre",
    'website': "www.libre.ec",
    'depends': ['stock',
                'stock_inventory_discrepancy',
                'stock_picking_template',
                ],
    'data': [
        'views/stock.xml',
        # 'security/ir.model.access.csv',
        ],
    'qweb': [
    ],
    'installable': True,
}
