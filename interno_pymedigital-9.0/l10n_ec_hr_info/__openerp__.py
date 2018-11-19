#!/usr/bin/env python
# -*- coding: utf-8 -*-

{
    'name': "Extra employee information",
    'summary': """
        Manage Extra employee information""",
    'category': "Localization/HR",
    'description': """
        Extra Information:

        - Work Experience
        - Academic Training
    """,

    'author': "edison@disroot.org",
    'website': "",
    'version': '9.0.0.3',
    'depends': [
        'base',
        'hr',
        'l10n_ec_hr_payroll'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_view.xml',
        'views/hr_academic_training_view.xml',
        'views/hr_work_experience_view.xml',
    ],
    'demo': [],
}
