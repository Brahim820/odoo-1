#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import logging
import StringIO
import time

from openerp import _, api, fields, models
from openerp.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    import pandas as pd
except ImportError:
    _logger.error("The module pandas can't be loaded, try: pip install pandas")

try:
    import xlrd
except ImportError:
    _logger.error("The module xlrd can't be loaded, try: pip install xlrd")

try:
    import xlsxwriter
except ImportError:
    _logger.error(
        "The module xlsxwriter can't be loaded, try: pip install xlsxwriter")


class WizardHrPayslipNews(models.TransientModel):
    """
    Generate and Imports news from Template
    """
    _name = 'wizard.hr.payslip.news'
    _description = __doc__

    employee_ids = fields.Many2many('hr.employee', 'hr_employee_wiz_news',
                                    'wiz_id', 'employee_id', _('Employees'))
    name = fields.Char(_('Name'))
    date = fields.Date('Register Date')
    file_template = fields.Binary(_('Template'))
    file_upload = fields.Binary(_('Template'))
    approve_news = fields.Boolean(_('Approve news'))

    line_ids = fields.One2many(
        'wizard.hr.payslip.news.line', 'wiz_id', string=_("Salary Rules"))
    option = fields.Selection([('export', _('Export Template')),
                               ('import', _('Import Template'))], string=_('Option'), default='export')
    state = fields.Selection([('draft', _('Draft')),
                              ('exported', _('Exported'))], string='State', default='draft')
    payroll_type = fields.Many2one(
        'hr.payslip.type', string='Payroll Type')

    @api.multi
    def generate_template(self):
        for row in self:
            rules = []
            if not row.line_ids:
                raise UserError(
                    _('Please select at least one salary rule to generate the template!!'))
            for rule in row.line_ids:
                rules.append('%s|%s' % (rule.name, rule.rule_id.code))
            employee_data = []
            file_data = StringIO.StringIO()
            xbook = xlsxwriter.Workbook(file_data, {'in_memory': True})
            xsheet = xbook.add_worksheet('News')
            header = [_('Identification'), _('Passport'), _('Name')] + rules
            if not row.employee_ids:
                raise UserError(
                    _('Please select at least one employee to generate the template!!'))
            for hr in row.employee_ids:
                data = []
                data.insert(0, hr.identification_id or '')
                data.insert(1, hr.passport_id or '')
                data.insert(2, hr.name)
                employee_data.append(data + [0.0 for x in rules])
                xsheet.write_row(0, 0, header)
            for line in range(0, len(employee_data)):
                xsheet.write_row(line + 1, 0, employee_data[line])
            xbook.close()
            out = base64.encodestring(file_data.getvalue())
            row.write({'name': _('News_Template.xlsx'),
                       'file_template': out, 'state': 'exported'})
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wizard.hr.payslip.news',
            'view_id': False,
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    @api.multi
    def import_template(self):
        employee_obj = self.env['hr.employee']
        news_obj = self.env['hr.payslip.news']
        rule_obj = self.env['hr.salary.rule']
        news_data = []
        for row in self:
            if not row.file_upload:
                raise UserError(_('Please Select file to import'))
            xdata = base64.b64decode(row.file_upload)
            xbook = xlrd.open_workbook(file_contents=xdata)
            df = pd.read_excel(xbook, "News", engine="xlrd")
            state = 'approved' if row.approve_news else 'draft'
            for index, y in df.iterrows():
                identification = '{:0>10}'.format(int(y[0]))
                employee_id = employee_obj.search([
                    '|', ('identification_id', '=', identification), ('passport_id', '=', y[1])])
                if not employee_id:
                    employee_id = employee_obj.with_context(show_unemployed=True).search([
                        '|', ('identification_id', '=', identification), ('passport_id', '=', y[1])])
                data = y.to_dict()
                if not employee_id:
                    raise UserError(_('Employee not found: {}'.format(y[2])))
                for key in data:
                    if key not in ['passport', 'Nro. Pasaporte', 'identification', 'Nro. Identificación', 'name', 'Nombre']:
                        if data[key] > 0:
                            news_name, news_code = key.split(
                                '|')[0], key.split('|')[1]
                            rule_id = rule_obj.search(
                                [('code', '=', news_code)])
                            news_data.append({
                                'name': news_name,
                                'date': row.date,
                                'rule_id': rule_id.id,
                                'payroll_type': row.payroll_type.id,
                                'employee_id': employee_id.id,
                                'amount': data[key],
                                'state': state
                            })
        for new in news_data:
            news_obj.create(new)
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'tree,from',
            'res_model': 'hr.payslip.news',
            'view_id': False,
            'res_id': False,
            'type': 'ir.actions.act_window'
        }


class WizardHrPayslipNewsLine(models.TransientModel):
    """
    Salary Rule detail
    """
    _name = 'wizard.hr.payslip.news.line'
    _description = __doc__

    wiz_id = fields.Many2one('wizard.hr.payslip.news', string=_('Wizard'))
    name = fields.Char(_('Reason'), required=True)
    rule_id = fields.Many2one(
        'hr.salary.rule', string=_("Salary Rule"), required=True)
