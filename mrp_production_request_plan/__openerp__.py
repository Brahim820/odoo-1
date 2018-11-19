# -*- coding: utf-8 -*-
{
    'name': "MRP production request plan",
    'version': '9.0.1.0.',
    'author': "Fabrica de software libre",
    'website': "www.libre.ec",
    'depends': ['mrp',
                'mrp_routing_capacity',
                'mrp_production_request',
                ],
    'data': [
        'views/mrp_production_request_view.xml',
        'wizards/mrp_production_request_create_mo_view.xml'
        ],
    'qweb': [
    ],
    'installable': True,
}
