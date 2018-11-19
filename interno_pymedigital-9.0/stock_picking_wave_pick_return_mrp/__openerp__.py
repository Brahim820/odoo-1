# -*- coding: utf-8 -*-
{
    'name': "Stock picking wave pick return",
    'version': '9.0.1.0.0',
    'author': "Fabrica de software libre",
    'website': "www.libre.ec",
    'depends': ['mrp',
                'stock',
                'stock_picking_wave',
                'base_pick_return',
                'pick_return_mrp',
                'stock_picking_wave_management',
                ],
    'data': [
        'views/stock.xml',
        ],
    'qweb': [
    ],
    'installable': True,
}
