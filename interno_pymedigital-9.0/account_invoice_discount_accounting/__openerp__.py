# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Invoice Discount Accounting',
    'version': '9.0.1.0.0',
    'category': 'Account',
    'author': 'Fábrica de Software Libre, '
              'Odoo Community Association (OCA)',
    'website': 'https://odoo-community.org',
    'license': 'AGPL-3',
    'summary': 'Add the discount to the account move.',
    'depends': [
        'account',
        'account_invoice_discount_amount',
        'account_custom_group_invoice_lines',
    ],
    'data': [
        'views/res_company.xml',
    ],
    'installable': True,
}
