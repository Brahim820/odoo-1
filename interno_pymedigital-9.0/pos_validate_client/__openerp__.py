# -*- coding: utf-8 -*-
{
    'name': "Pos Validate Client",

    'summary': """
        It alerts for the customer selection before Payment.""",

    'description': """
        It alerts for the customer selection before Payment.
    """,

    'author': "DRC Systems India Pvt. Ltd.",
    'website': "http://www.drcsystems.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Point Of Sale',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['base','point_of_sale'],

    # always loaded
    'data': [
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],

    'installable': True,
    'auto_install': False,
}
