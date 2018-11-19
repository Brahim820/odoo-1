#!/usr/bin/env python
# -*- coding: utf-8 -*-

from openerp import _, api, fields, models
from openerp.exceptions import UserError


class HrPayslipNews(models.Model):
    """
    Manage income, expenses to payslip
    """
    _name = "hr.payslip.news"
    _description = __doc__

    name = fields.Char(_('Description'), readonly=True, required=True,
                       states={'draft': [('readonly', False)]})
    employee_id = fields.Many2one('hr.employee', string=_('Employee'),
                                  required=True, readonly=True,
                                  states={'draft': [('readonly', False)]})
    department_id = fields.Many2one('hr.department', string=_(
        'Department'), related='employee_id.department_id', store=True)
    rule_id = fields.Many2one('hr.salary.rule', string=_('Salary Rule'),
                              readonly=True, required=True,
                              states={'draft': [('readonly', False)]})
    loan_id = fields.Many2one(
        'hr.payslip.loans', string=_('Loan'), ondelete='cascade')
    date = fields.Date(_('Date'), readonly=True,
                       states={'draft': [('readonly', False)]})
    amount = fields.Float(_('Amount'), readonly=True, required=True,
                          states={'draft': [('readonly', False)]})
    quantity = fields.Char(_('Quantity'), default='1')
    state = fields.Selection([('draft', _('Draft')),
                              ('approved', _('Approved')),
                              ('done', _('Done'))], string=_('State'),
                             default='draft')
    payroll_type = fields.Many2one(
        'hr.payslip.type', string='Payroll Type', required=True)

    @api.one
    def approved_new(self):
        self.state = 'approved'

    @api.multi
    def unlink(self):
        delete = True
        for row in self:
            if row.state in ['approved', 'done']:
                delete = False
        if not delete:
            raise UserError(_('Can not delete a record in an approved state!'))
        return super(HrPayslipNews, self).unlink()
