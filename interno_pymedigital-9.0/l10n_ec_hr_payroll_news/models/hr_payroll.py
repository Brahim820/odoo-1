#!/usr/bin/env python
# -*- coding: utf-8 -*-

from openerp import _, api, fields, models


class HrPayslipInput(models.Model):
    """
    Add news links to hr.payslip.input
    """
    _inherit = ['hr.payslip.input']
    _description = __doc__

    new_id = fields.Many2one(
        'hr.payslip.news',
        string=_('New'),
        ondelete='cascade')
    overtime_id = fields.Many2one(
        'hr.payslip.overtime.line',
        string=_('New'),
        ondelete='cascade')
    quantity = fields.Char(_('Quantity'))


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    @api.one
    def compute_sheet(self):
        self.slip_ids.compute_inputs()
        return super(HrPayslipRun, self).compute_sheet()


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.multi
    def update_sheet(self):
        self.compute_inputs()
        return super(HrPayslip, self).update_sheet()

    @api.multi
    def process_sheet(self):
        for row in self:
            for line in row.input_line_ids:
                if line.new_id:
                    line.new_id.write({'state': 'done'})
                if line.overtime_id:
                    line.overtime_id.write({'state': 'done'})
                    line.overtime_id.overtime_id.write({'state': 'done'})
        return super(HrPayslip, self).process_sheet()

    @api.multi
    def undo_sheet(self):
        for row in self:
            for line in row.input_line_ids:
                if line.new_id:
                    line.new_id.write({'state': 'approved'})
                if line.overtime_id:
                    line.overtime_id.write({'state': 'draft'})
                    line.overtime_id.overtime_id.write({'state': 'draft'})
        return super(HrPayslip, self).undo_sheet()

    @api.multi
    def compute_inputs(self):
        for payslip in self:
            old_input_ids = payslip.mapped('input_line_ids')
            if old_input_ids:
                # delete old input lines
                old_input_ids.unlink()

            contract_ids = payslip.contract_id.ids or \
                self.get_contract(payslip.employee_id,
                                  payslip.date_from, payslip.date_to)
            inputs = [(0, 0, inputs) for inputs in self.with_context(payroll_type=payslip.payroll_type.id).get_inputs(
                contract_ids, payslip.date_from, payslip.date_to)]
            payslip.write({'input_line_ids': inputs})
        return True

    @api.model
    def get_inputs(self, contract_ids, date_from, date_to):
        try:
            payroll_type = self._context.get('payroll_type', False)[0]
        except TypeError:
            payroll_type = self._context.get('payroll_type', False)
        contract_obj = self.env['hr.contract']
        res = super(HrPayslip, self).get_inputs(
            contract_ids, date_from, date_to)
        news_obj = self.env['hr.payslip.news']
        overtime_obj = self.env['hr.payslip.overtime.line']
        for contract in contract_obj.browse(contract_ids):
            news_ids = news_obj.search([('date', '>=', date_from),
                                        ('date', '<=', date_to),
                                        ('payroll_type', '=', payroll_type),
                                        ('employee_id', '=',
                                         contract.employee_id.id),
                                        ('state', '=', 'approved')])
            for new in news_ids:
                inputs = {
                    'name': str(new.name or new.rule_id.name).upper(),
                    'code': new.rule_id.code,
                    'contract_id': contract.id,
                    'quantity': new.quantity,
                    'new_id': new.id,
                    'amount': new.amount,
                }
                res += [inputs]
            overtime_ids = overtime_obj.search([('date', '>=', date_from),
                                                ('date', '<=', date_to),
                                                ('employee_id', '=',
                                                 contract.employee_id.id),
                                                ('state', '=', 'approved')])

            for over in overtime_ids:
                if over.overtime_025:
                    inputs = {
                        'name': _('HOURS NIGHT SHIFT (25%)'),
                        'code': 'HE025',
                        'contract_id': contract.id,
                        'overtime_id': over.id,
                        'quantity': over.overtime_025,
                        'amount': over.hour_cost * over.overtime_025 * 1.75
                    }
                    res += [inputs]
                if over.overtime_050:
                    inputs = {
                        'name': _('OVERTIME (50%)'),
                        'code': 'HE050',
                        'contract_id': contract.id,
                        'overtime_id': over.id,
                        'quantity': over.overtime_050,
                        'amount': over.hour_cost * over.overtime_050 * 1.50
                    }
                    res += [inputs]
                if over.overtime_100:
                    inputs = {
                        'name': _('EXTRA HOURS (100%)'),
                        'code': 'HE100',
                        'contract_id': contract.id,
                        'overtime_id': over.id,
                        'quantity': over.overtime_100,
                        'amount': over.hour_cost * over.overtime_100 * 2.00
                    }
                    res += [inputs]
        return res
