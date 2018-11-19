# -*- coding: utf-8 -*-
{
    'name': "Stock pricking from POS board",

    'summary': """
        Allows to generate stock pickings from pos.""",

    'author': "Fábrica de Software Libre",
    'website': "www.libre.ec",

    'category': 'Point Of Sale',
    'version': '9.0.0.0.1',

    'depends': ['base','point_of_sale', 'stock'],

    # always loaded
    'data': [
        'views/point_of_sale.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],

    'installable': True,
    'auto_install': False,
}
