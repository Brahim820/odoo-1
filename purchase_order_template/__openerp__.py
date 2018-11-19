# -*- coding: utf-8 -*-
{
    'name': "Purchase order template",
    'version': '9.0.1.0.',
    'author': "Fabrica de software libre",
    'website': "www.libre.ec",
    'depends': ['purchase',
                ],
    'data': [
        'wizards/complete_from_template_view.xml',
        'views/purchase.xml',
        'security/ir.model.access.csv',
        ],
    'qweb': [
    ],
    'installable': True,
}
