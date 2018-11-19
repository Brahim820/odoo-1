# -*- coding: utf-8 -*-

{
    'name': 'Equipment Maintenance',
    'version': '0.1.0',
    'category': '',
    'summary': 'Equipment Maintenance',
    'description': """
    Equipment Maintenance
    """,
    'author': 'Jonathan Finlay <jfinlay@riseup.net>',
    'depends': [
        'hr_equipment',
        'account_asset',
        'resource',
        'sale',
        'stock'
    ],
    'data': [
        'data/equipment_data.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'views/maintenance_team_view.xml',
        'views/hr_equipment_view.xml',
        'views/maintenance_report_view.xml',
        'views/planned_equipment.xml',
    ],

    'application': False,
    'installable': True,
}