# -*- coding: utf-8 -*-
{
    'name': "Payroll account map",
    'summary': """
        Salary rules account mapping""",
    'category': "Localization/Payroll",
    'description': """
        Map accounts to salary rules:

        - Advances
        - Payroll
        - Loans
    """,
    'license': 'AGPL-3',
    'author': "jfinlay@riseup.net",
    'website': "http://www.lalibre.net",
    'version': '0.1',
    'depends': ['hr_payroll_account', 'l10n_ec_hr_payroll', 'l10n_ec_niif_base'],
    'data': [
        'data/hr_data.xml',
        'data/account_salary_rules_map.xml',
    ],
    'demo': [],
}