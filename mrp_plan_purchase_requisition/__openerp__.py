# -*- coding: utf-8 -*-
{
    'name': "MRP plan wizard purchase requisition",
    'version': '9.0.1.0.',
    'author': "Fabrica de software libre",
    'website': "www.libre.ec",
    'depends': ['mrp',
                'mrp_plan_wizard',
                'purchase_requisition',
                ],
    'data': [
        'views/material_plan_wizard.xml',
        ],
    'qweb': [
    ],
    'installable': True,
}
