# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Invoice Import',
    'version': '9.0.1.0.0',
    'category': 'Account',
    'author':
              'Fábrica de Software Libre, '
              'Odoo Community Association (OCA)',
    'website': 'https://odoo-community.org',
    'license': 'AGPL-3',
    'summary': 'Import Invoices',
    'depends': [
        'account',
    ],
    'data': [
        'wizard/account_invoice_import_wizard_view.xml',
    ],
    'installable': True,
}
