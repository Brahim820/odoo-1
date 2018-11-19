# -*- coding: utf-8 -*-
{
    'name': "Contract invoice consumption",

    'summary': """
        .""",

    'author': "Fábrica de Software Libre",
    'website': "www.libre.ec",

    'category': 'Event',
    'version': '9.0.0.0.2',

    'depends': ['contract', 'contract_variable_quantity'],

    # always loaded
    'data': [
        'views/contract.xml',
        'data/contract_line_qty_formula.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],

    'installable': True,
    'auto_install': False,
}
