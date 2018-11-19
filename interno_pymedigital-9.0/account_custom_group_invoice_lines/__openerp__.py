# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Custom Group invoice lines',
    'version': '9.0.1.0.0',
    'category': 'Account',
    'author': 'Fábrica de Software Libre, '
              'Odoo Community Association (OCA)',
    'website': 'https://odoo-community.org',
    'license': 'AGPL-3',
    'summary': 'Allow to select the fields to use in invoice line group',
    'depends': [
        'account',
    ],
    'data': [
        'views/account.xml',
    ],
    'installable': True,
}
