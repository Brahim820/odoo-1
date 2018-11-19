# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Luis M. Ontalba
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Bank statement import',
    'version': '9.0.1.0.0',
    'category': 'Accounting',
    'author': 'Fabrica de Software Libre, '
              'Odoo Community Association (OCA)',
    'website': 'https://www.fslibre.com',
    'depends': [
        'account',
        'account_bank_statement_import_move_line',
    ],
    'data': [
        'views/account_bank_statement_view.xml'
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}
