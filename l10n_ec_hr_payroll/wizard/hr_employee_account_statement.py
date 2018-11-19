#!/usr/bin/env python
# -*- coding: utf-8 -*-

from openerp import _, api, fields, models


class HrEmployeeAccountStatement(models.TransientModel):
    _name = "hr.employee.account.statement"

    date_from = fields.Date(_("Date From"))
    date_to = fields.Date(_("Date To"))
    option = fields.Selection(
        [
            ("all", _("All")),
            ("employees", _("Employees")),
            ("departments", _("Departments")),
        ],
        string=_("Option"),
        default="all",
    )
    employee_ids = fields.Many2many("hr.employee", string=_("Employee"))
    department_ids = fields.Many2many("hr.department", string=_("Department"))
