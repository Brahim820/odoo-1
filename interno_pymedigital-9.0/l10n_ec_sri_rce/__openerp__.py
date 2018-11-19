# -*- coding: utf-8 -*-
{
    'name': "SRI - Recepción de comprabantes electronicos",
    'summary': """SRI Emisión de comprobantes electrónicos off-line.""",
    'version': '9.0.1.0.0',
    'author': "Fabrica de Software Libre,Odoo Community Association (OCA)",
    'maintainer': 'Fabrica de Software Libre',
    'website': 'http://www.libre.ec',
    'license': 'AGPL-3',
    'category': 'Account',
    'depends': [
        'base',
        'l10n_ec_sri_ece',
    ],
    'data': [
        'wizards/ce_import_view.xml',
        'views/account_invoice.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
}
