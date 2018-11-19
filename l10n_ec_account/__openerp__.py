# -*- coding: utf-8 -*-
{
    'name': "Ecuador Accounting",
    'summary': """Add local accounting requirements.""",
    'version': '9.0.1.0.0',
    'author': "Fabrica de Software Libre,Odoo Community Association (OCA)",
    'maintainer': 'Fabrica de Software Libre',
    'website': 'http://www.libre.ec',
    'license': 'AGPL-3',
    'category': 'Account',
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'views/account_move.xml',
        'views/account_invoice.xml',
        'views/report_financial.xml',
        'views/report_account_move.xml',
        'reports/account_move_line_report_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'test': [],
    'installable': True,
}
