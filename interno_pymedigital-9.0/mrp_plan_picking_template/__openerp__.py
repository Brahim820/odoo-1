# -*- coding: utf-8 -*-
{
    'name': "MRP Plan using picking templates",
    'version': '9.0.1.0.',
    'author': "Fabrica de software libre",
    'website': "www.libre.ec",
    'depends': ['stock',
                'mrp',
                'mrp_plan_wizard',
                'stock_picking_template',
                ],
    'data': [
        'views/material_plan_wizard.xml',
        ],
    'qweb': [
    ],
    'installable': True,
}
