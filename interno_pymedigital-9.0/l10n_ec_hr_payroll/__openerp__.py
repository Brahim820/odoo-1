# -*- coding: utf-8 -*-
{
    'name': "Payroll for Ecuador",
    'summary': """
        Human resources managment for Ecuador""",
    'category': "Localization/Payroll",
    'description': """
        Payroll management for Ecuador:

        - Adelantos
        - Payroll
        - Prestamos
    """,

    'author': "jfinlay@riseup.net",
    'website': "http://www.lalibre.net",
    'version': '9.0.0.3',
    'depends': [
        'base',
        'hr',
        'hr_contract',
        'hr_payroll',
        'hr_payroll_account',
        'hr_holidays',
        'hr_recruitment',
        'l10n_ec_sri',
        'l10n_ec_payment',
        'web_readonly_store',
        'report_xlsx',
    ],
    'data': [
        'security/hr_security.xml',
        'security/ir.model.access.csv',
        'data/hr_salary_rule_category.xml',
        'data/hr_salary_rule_alw.xml',
        'data/hr_salary_rule_ded.xml',
        'data/hr_salary_rule_prov.xml',
        'data/hr_salary_rule_liq.xml',
        'data/hr_payroll_structure.xml',
        'data/hr_contract_finish.xml',
        'data/hr_contract_type.xml',
        'data/res_company_data.xml',
        'data/hr_deduction.xml',
        'data/hr_sri_retention.xml',
        'data/hr.holidays.status.csv',
        'data/hr.payslip.type.csv',
        'views/res_company_view.xml',
        'views/res_partner_view.xml',
        'views/hr_contract_view.xml',
        'views/hr_employee_view.xml',
        'views/hr_job_view.xml',
        'views/hr_department_view.xml',
        'views/hr_payroll_view.xml',
        'views/hr_holidays.xml',
        'views/hr_sri_view.xml',
        'wizard/hr_contract_finish.xml',
        'wizard/wizard_hr_contract_update_view.xml',
        'wizard/wizard_hr_salary_rule_map_view.xml',
        'wizard/wizard_hr_payroll_print.xml',
        'wizard/wizard_hr_payroll_spi.xml',
        'wizard/hr_payroll_payslips_by_employees_views.xml',
        'data/update_name.xml',
        'report/hr_payslip_report.xml',
        'report/hr_payslip_report_xlsx.xml'
    ],
    'demo': [],
}
