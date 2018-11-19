# -*- coding: utf-8 -*-
{
    'name': "SRI - Validador del ATS",
    'summary': """Valida las facturas para asegurar su coherencia con el ATS.""",
    'version': '9.0.1.0.0',
    'author': "Fabrica de Software Libre,Odoo Community Association (OCA)",
    'maintainer': 'Fabrica de Software Libre',
    'website': 'http://www.libre.ec',
    'license': 'AGPL-3',
    'category': 'tools',
    'depends': [
        'l10n_ec_sri',
    ],
    'data': [
        'views/account_invoice.xml',
        'views/tax_form.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
}
