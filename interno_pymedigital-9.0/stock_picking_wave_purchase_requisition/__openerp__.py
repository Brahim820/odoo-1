# -*- coding: utf-8 -*-
{
    'name': "Purchase requisition on wave management.",
    'version': '9.0.1.0.',
    'author': "Fabrica de software libre",
    'website': "www.libre.ec",
    'depends': ['stock_picking_wave_management',
                'purchase_requisition',
                ],
    'data': [
        'views/purchase_requisition.xml',
        'views/stock.xml',
    ],
    'external_dependencies': {
    },

    'qweb': [
    ],
    'installable': True,
}
