# -*- coding: utf-8 -*-
{
    'name': "Pick and return with template",
    'version': '9.0.1.0.1',
    'author': "Fabrica de software libre",
    'website': "www.libre.ec",
    'depends': [
        'stock',
        'stock_picking_template',
        'base_pick_return',
    ],
    'data': [
        'wizards/stock_pick_return_wizard_view.xml',
        ],
    'qweb': [
    ],
    'installable': True,
}
