# -*- coding: utf-8 -*-
{
    'name': 'MRP Product duplication',
    "author": "Fábrica de Software Libre",
    'summary': """
         MRP Product duplication with his variants, 
         bill of materials and all the main issues 
         related to Manufacturing""",

    'category': 'Manufacturing',
    "version": "9.0.0.0.1",

    'depends': ['mrp'],
    'data': [
        'views/product_view.xml',
        'wizards/product_duplication_wzd_view.xml',
    ],
}
