# -*- coding: utf-8 -*-

{
    'name': 'Production Cancel Reason',
    'version': '9.0.0.0.1',
    'author': 'Fábrica de Software Libre, '
              ' Odoo Community Association (OCA), ',
    'category': 'Manufacturing',
    'license': 'AGPL-3',
    'website': "http://fslibre.com",
    'depends': [
        'mrp',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/cancel_reason.xml',
        'wizards/cancel_reason_view.xml',
        'views/production.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
