# -*- coding: utf-8 -*-
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Account bank match number',
    'version': '9.0.3.0.8',
    'category': 'Accounting',
    'author': 'Fábrica de Software Libre, '
              'Odoo Community Association (OCA)',
    'website': 'https://www.fslibre.com',
    'depends': [
        'account',
        #  TODO: Eliminar dependencia a l10n_ec_payment después de actualizar.
        'l10n_ec_payment',
    ],
    'data': [
        'views/account_account.xml',
        'views/account_payment.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}
