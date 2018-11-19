# -*- coding: utf-8 -*-
from datetime import datetime

from openerp import _, api, fields, models, tools


class hr_payslip_input(models.Model):
    _inherit = ['hr.payslip.input']
    _description = 'Payslip Input'

    novedad_id = fields.Many2one(
        'hr.novedad.line',
        string='Novedad',
        ondelete='cascade')

_STATE = [('draft', 'Borrador'), ('pendiente', 'Pendiente'), ('pagado', 'Pagado')]


class hr_novedad(models.Model):
    _name = 'hr.novedad'
    _description = 'Regsitro de Novedades en el Rol de Pagos'

    @api.multi
    def write(self, vals):
        data = {}
        if vals.get('rule_id'):
            data.update({'rule_id': vals['rule_id']})
        if vals.get('name'):
            data.update({'name': vals['name']})
            for i in self:
                if i.line_ids:
                    for j in i.line_ids:
                        j.write(data)
        return super(hr_novedad, self).write(vals)

    @api.multi
    def pendiente(self):
        for this in self:
            this.write({'state': 'pendiente'})
            if this.line_ids:
                for i in this.line_ids:
                    i.write({'state': 'pendiente'})

    name = fields.Char(
        string=u'Descripción',
        size=128,
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]})
    date = fields.Date(
        string='Fecha',
        readonly=True,
        required=True,
        default=datetime.now(),
        states={'draft': [('readonly', False)]})
    rule_id = fields.Many2one(
        'hr.salary.rule',
        string='Regla Salarial',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]})
    line_ids = fields.One2many(
        'hr.novedad.line',
        'novedad_id',
        string='Detalle',
        readonly=True,
        states={'draft': [('readonly', False)]})
    state = fields.Selection(_STATE, string='State', default='draft')


class hr_novedad_line(models.Model):
    _name = 'hr.novedad.line'
    _description = 'Regsitro de Novedades en el Rol de Pagos'

    @api.model
    def create(self, values):
        vals = {}
        if values.get('novedad_id'):
            novedad_obj = self.env['hr.novedad']
            novedad_data = novedad_obj.browse(values['novedad_id'])
            vals = {
                'novedad_id': values['novedad_id'],
                'employee_id': values['employee_id'],
                'rule_id': novedad_data.rule_id.id,
                'amount': values['amount'],
                'date': novedad_data.date,
                'state': novedad_data.state,
                'name': novedad_data.name
            }
        return super(hr_novedad_line, self).create(vals or values)

    @api.multi
    def write(self, vals):
        res = super(hr_novedad_line, self).write(vals)
        return res

    @api.multi
    def pendiente(self):
        for this in self:
            this.write({'state': 'pendiente'})

    name = fields.Char(
        string=u'Descripción',
        size=128,
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]})
    date = fields.Date(
        string='Fecha',
        readonly=True,
        required=True,
        default=datetime.now(),
        states={'draft': [('readonly', False)]})
    employee_id = fields.Many2one(
       'hr.employee',
       string='Empleado',
       required=True,
       readonly=True,
       states={'draft': [('readonly', False)]})
    amount = fields.Float(
       string='Value',
       required=True,
       readonly=True,
       states={'draft': [('readonly', False)]})
    rule_id = fields.Many2one(
       'hr.salary.rule',
       string='Regla Salarial',
       required=True,
       readonly=True,
       states={'draft': [('readonly', False)]})
    novedad_id = fields.Many2one(
       'hr.novedad',
       string='Novedad',
       ondelete='cascade')
    state = fields.Selection(_STATE, string='State', readonly=True, default='draft')
