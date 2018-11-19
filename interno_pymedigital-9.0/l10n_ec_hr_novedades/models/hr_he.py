# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools, _
from datetime import datetime


class hr_he(models.Model):
    _name = 'hr.he'
    _description = 'Registro de Horas Extras'

    @api.multi
    def procesar(self):
        for this in self:
            this.write({'state': 'done'})
            if this.line_ids:
                for i in this.line_ids:
                    i.write({'state': 'done'})

    name = fields.Char(string=u'Descripción', size=35, default='Registro de Horas Extras')
    date = fields.Date(
        string='Fecha',
        states={'done': [('readonly', True)]},
        required=True,
        default=datetime.now())
    line_ids = fields.One2many(
        'hr.he.line',
        'he_id',
        string='Detail',
        states={'done': [('readonly', True)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done')],
        string='State',
        select=True,
        readonly=True,
        default='draft')


class hr_he_line(models.Model):
    _name = 'hr.he.line'
    _description = 'Detalle de Horas Extras'

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        contract_obj = self.env['hr.contract']
        if self.employee_id:
            contract_data = contract_obj.browse(self.employee_id.id)
            if contract_data:
                self.wage = contract_data.wage
                self.valor_hora = (float(contract_data.wage) / 240)
        return

    @api.multi
    @api.depends('hora_125', 'hora_150', 'hora_200')
    def _calcular(self):
        total_125 = 0.0
        total_150 = 0.0
        total_200 = 0.0
        for i in self:
            if i.hora_125 > 0:
                total_125 = i.valor_hora * i.hora_125 * 1.25
            if i.hora_150 > 0:
                total_150 = i.valor_hora * i.hora_150 * 1.50
            if i.hora_200 > 0:
                total_200 = i.valor_hora * i.hora_200 * 2.00
            self.total = total_125 + total_150 + total_200

    name = fields.Char(string=u'Descripción', size=12)
    he_id = fields.Many2one(
        'hr.he',
        string='Registro',
        ondelete='cascade')
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        ondelete='cascade')
    date = fields.Date(
        string='Fecha',
        states={'done': [('readonly', True)]},
        required=True,
        default=datetime.now())
    wage = fields.Float(string='Wage', readonly=True)
    valor_hora = fields.Float(string='Hour Cost', readonly=True)
    hora_100 = fields.Float(string='Horas Normales', readonly=True, required=True, default='80')
    hora_125 = fields.Float(string='Horas al 25%', required=True, default='0')
    hora_150 = fields.Float(string='Horas al 50%', required=True, default='0')
    hora_200 = fields.Float(string='Horas al 100%', required=True, default='0')
    total = fields.Float(string='Total', compute='_calcular', default='0')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done')],
        string='State',
        select=True,
        readonly=True,
        default='draft')
