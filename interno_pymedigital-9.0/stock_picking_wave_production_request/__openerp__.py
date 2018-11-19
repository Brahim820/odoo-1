# -*- coding: utf-8 -*-
{
    'name': "Production request on wave management.",
    'version': '9.0.1.0.',
    'author': "Fabrica de software libre",
    'website': "www.libre.ec",
    'depends': [
        'stock_picking_wave_management',
        'mrp_production_request',
        'stock_available_unreserved',
    ],
    'data': [
        'wizard/plan_production_request_view.xml',
        'views/mrp_production_request.xml',
        'views/stock.xml',
    ],
    'external_dependencies': {
    },

    'qweb': [
    ],
    'installable': True,
}
