# -*- coding: utf-8 -*-
{
    'name': "ECUADOR EMISION DE COMPROBANTES ELECTRONICOS - STOCK",
    'summary': """Stock modifications for SRI Ecuador.""",
    'version': '9.0.1.0.0',
    'author': "Fabrica de Software Libre,Odoo Community Association (OCA)",
    'maintainer': 'Fabrica de Software Libre',
    'website': 'http://www.fslibre.com',
    'license': 'AGPL-3',
    'category': 'Stock',
    'depends': [
        'base',
        'delivery',
        'stock',
        'l10n_ec_sri',
        'l10n_ec_sri_ece',
        'base_mail_custom_attachment',
    ],
    'data': [
        'views/res_company.xml',
        'views/res_partner.xml',
        'views/res_users.xml',
        'views/delivery.xml',
        'wizard/wizard_carrier_info_view.xml',
        'views/stock_picking.xml',
        'views/stock_picking_report.xml',
        'security/ir.model.access.csv',
        'data/stock_action_data.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
}
