# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account account code structure',
    'version': '9.0.0.0.1',
    'category': 'Account',
    'author': 'Fábrica de Software Libre, '
              'Odoo Community Association (OCA)',
    'website': 'https://odoo-community.org',
    'license': 'AGPL-3',
    'summary': 'Add a structure the code of account.account.',
    'depends': [
        'account',
    ],
    'data': [
        'views/account.xml',
        #'views/res_company.xml',
    ],
    'installable': True,
}
