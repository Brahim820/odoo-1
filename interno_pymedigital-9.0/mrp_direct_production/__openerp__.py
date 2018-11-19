# -*- coding: utf-8 -*-
{
    'name': "MRP Direct Production",

    'summary': """
        MRP Direct Production""",

    'description': """Allow the user to make the production directly without a wizard, after the materials has been reserved.
    
    Adding buttons on TREE view for RESERVE and DIRECT PRODUCTION.""",

    'author': "Fabrica de Software Libre",
    'maintainer': 'Fabrica de Software Libre',
    'website': 'http://www.fslibre.com',
    'license': 'AGPL-3',
    'category': 'Manufacturing',
    'version': '9.0.1.0.1',
    'depends': [
        'base',
        'mrp',
    ],
    'data': [
        'views/mrp_views.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}