# -*- coding: utf-8 -*-
{
    'name': "account_xls_report",

    'summary': """
        Exportación de reportes como hojas de calculo XLS""",

    'description': """
        Exportación de reportes como hojas de calculo XLS:
        - Account reports
    """,

    'author': "jfinlay@riseup.net",
    'website': "http://www.lalibre.net",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Account',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['report_xlsx', 'account'],

    # always loaded
    'data': [
        # 'views/account_view.xml',
        'views/assets.xml',
        'views/account_report_aged_partner_balance_view.xml',
        'views/account_balance_view.xml',
        'views/account_financial_report_view.xml',
        'views/account_report_trial_balance_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
}
