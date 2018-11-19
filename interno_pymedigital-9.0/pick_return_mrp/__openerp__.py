# -*- coding: utf-8 -*-
{
    'name': "MRP Raw material pick and return",
    'version': '9.0.1.0.0',
    'author': "Fabrica de software libre",
    'website': "www.libre.ec",
    'depends': [
        'mrp',
        'stock',
        'base_pick_return',
    ],
    'data': [
        'wizards/mrp_pick_return_wizard_view.xml',
        'views/mrp.xml',
        'views/stock.xml',
    ],
    'qweb': [],
    'installable': True,
}
