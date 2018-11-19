# -*- coding: utf-8 -*-
{
    'name': "GESTIÓN DE COMPRAS ECUADOR - SRI",
    'summary': """Purchase modifications for SRI Ecuador.""",
    'version': '9.0.1.0.0',
    'author': "Fabrica de Software Libre,Odoo Community Association (OCA)",
    'maintainer': 'Fabrica de Software Libre',
    'website': 'http://www.fslibre.com',
    'license': 'AGPL-3',
    'category': 'Purchase',
    'depends': [
        'base',
        'purchase',
        'l10n_ec_sri',
    ],
    'data': [
        'views/purchase.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': True,
}
