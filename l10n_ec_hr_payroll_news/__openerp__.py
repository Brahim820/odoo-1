#!/usr/bin/env python
# -*- coding: utf-8 -*-

{
    'name': "Payroll News for Ecuador",
    'summary': '',
    'category': "Localization/Payroll",
    'description': """
Manage Income/Expenses in payslip
=================================
    """,
    'author': "edison@disroot.org",
    'website': '',
    'version': '0.1',
    'depends': [
        'base',
        'l10n_ec_hr_payroll',
        'web_readonly_store'
    ],
    'external_dependencies': {
        'python': [
            'pandas',
            'xlsxwriter',
            'xlrd',
        ]
    },
    'data': [
        'security/ir.model.access.csv',
        'views/hr_payroll_news_view.xml',
        'wizard/wizard_hr_payslip_overtime_view.xml',
        'views/hr_payroll_overtime_view.xml',
        'wizard/wizard_hr_payslip_news_view.xml',
        'views/hr_payroll_loans_view.xml',
        'views/res_company.xml'
    ],
    'demo': [],
    'installable': False,
}
