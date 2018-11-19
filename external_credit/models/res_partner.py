# -*- coding: utf-8 -*-
####################################################
# Parte del Proyecto LibreGOB: http://libregob.org #
# Licencia AGPL-v3                                 #
####################################################

from openerp import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    code = fields.Char(
        string='Code',
        required=True,
        help="EPMAPS identifier"
    )
    committee_groups = fields.Selection([
            ('ce','Comité de Empresa'),
            ('st','Sindicato Trabajadores'),
            ('se','Sindicato Empleados'),
            ('np','No pertenece'),
        ], default="np",
        string='Committee Groups',
        required=True,
        )

    credit_ids = fields.One2many(
        'credit.credit',
        'partner_id',
        string='Credits',
         )

    is_affiliate = fields.Boolean(string='Is affiliate?', )
    size = fields.Integer(string='Size', )

    entry_date = fields.Date(string='Entry date', )
    job_id = fields.Many2one('hr.employee', string='Job', )
    department_id = fields.Many2one('hr.employee', string='Area', )
    rmu_ids = fields.One2many(
        'res.partner.rmu',
        'partner_id',
        string='Rmus',
         )


    _sql_constraints = [
        ('code_uniq', 'UNIQUE (code)',  'You can not have two affiliates with the same code !')
    ]

class ResPartnerRmu(models.Model):
    _name = 'res.partner.rmu'
    _description = 'Res Partner Rmu'
    _order = 'id_desc'

    partner_id = fields.Many2one('res.partner', string='Partner', )

    year = fields.Char(string='Year', )

    rmu = fields.Float(
        string='Current Rmu',
        help="Current Unified monthly remuneration"
    )
    due_amount = fields.Float(string='Dues', compute="_compute_due_amount")

    @api.multi
    @api.depends('rmu')
    def _compute_due_amount(self):
        for r in self:
            if r.rmu < 1000:
                r.due_amount = 10
            elif r.rmu >= 1000:
                r.due_amount = r.rmu * 0.01


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    account_type = fields.Selection([
            ('1','Savings'),
            ('2','Current'),
        ], default="1",
        string='Account Type',
        )

