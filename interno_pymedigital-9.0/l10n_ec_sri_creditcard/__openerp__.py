# -*- coding: utf-8 -*-
{
    'name': "SRI Tarjeta de Credito",
    'summary': """Permite registar las retenciones realizadas con tarjeta de credito.""",
    'version': '9.0.1.0.0',
    'author': "Fabrica de Software Libre,Odoo Community Association (OCA)",
    'maintainer': 'Fabrica de Software Libre',
    'website': 'http://www.libre.ec',
    'license': 'AGPL-3',
    'category': 'Account',
    'depends': [
        'base',
        'account',
        'l10n_ec_sri',
    ],
    'data': [
        "views/account_invoice.xml",
        "data/sri/account.tax.csv",
    ],
    'demo': [],
    'test': [],
    'installable': True,
}
