# -*- coding: utf-8 -*-
{
    'name': "Contract invoice consumption asset",

    'summary': """
        .""",

    'author': "Fábrica de Software Libre",
    'website': "www.libre.ec",

    'category': 'Event',
    'version': '9.0.0.0.2',

    'depends': ['account',
                'contract_invoice_consumption',
                'account_asset',
                'base_mail_custom_attachment' ],

    # always loaded
    'data': [
        'views/asset.xml',
        'views/contract.xml',
        'views/account_invoice.xml',
        'security/ir.model.access.csv'
    ],
    'qweb': [],
    # only loaded in demonstration mode
    'demo': [
    ],

    'installable': True,
    'auto_install': False,
}
