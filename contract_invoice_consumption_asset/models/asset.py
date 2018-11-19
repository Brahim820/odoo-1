# -*- encoding: utf-8 -*-
from openerp import api, fields, models, _
from openerp.exceptions import UserError, RedirectWarning, ValidationError


class AccountAssetAssetConsumption(models.Model):
    _name = 'account.asset.asset.consumption'
    _order = 'date desc, id desc'

    @api.multi
    def unlink(self):
        for r in self:
            if r.state in ('confirmed', 'invoiced'):
                raise UserError(_(
                "Can't delete records in %s state."
                ) % (r.state,))
            return super(AccountAssetAssetConsumption, self).unlink()

    name = fields.Char(
        string='Name',
        related='asset_id.name',
        store=True,
    )

    voucher = fields.Binary(
        string='Voucher',
        attachment=True,
        readonly=True, states={'draft': [('readonly', False)]},
    )
    voucher_filename = fields.Char(string='Voucher filename', )

    asset_id = fields.Many2one(
        'account.asset.asset',
        string='Asset',
        required=True,
        readonly=True, states={'draft': [('readonly', False)]},
    )
    quantity = fields.Integer(
        string='Quantity',
        required=True,
        readonly=True, states={'draft': [('readonly', False)]},
    )

    description = fields.Text(
        string='Description',
        readonly=True,
        states={
            'draft': [('readonly', False)],
            'adjusted': [('required', True)],
            },
    )
    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        default=lambda self: self.env.user,
        readonly=True, states={'draft': [('readonly', False)]},
    )
    date = fields.Date(string='Date',
        required=True,
        default=fields.Date.context_today,
        readonly=True, states={'draft': [('readonly', False)]},
    )
    state = fields.Selection([
            ('draft','Draft'),
            ('confirmed','Confirmed'),
            ('invoiced', 'Invoiced'),
            ('adjusted','Adjusted'),
        ], default="draft",
        string='State',
        readonly=True,
    )

    counter_type_id = fields.Many2one(
        'asset.consumption.counter.type',
        string='Counter type',
        required=True,
        readonly=True, states={'draft': [('readonly', False)]},
    )

    invoice_line_ids = fields.Many2many(
        'account.invoice.line',
        'asset_consumption_line_invoice_line_rel',
        'asset_consumption_line_ids',
        'invoice_line_ids',
        string='Invoice lines',
         )

    @api.multi
    def button_state_draft(self):
        for line in self:
            line.write({'state': 'draft'})

    @api.multi
    def button_state_confirmed(self):
        for line in self:
            line.write({'state': 'confirmed'})


    @api.multi
    def button_state_adjustment(self):
        for line in self:
            line.write({'state': 'adjusted'})


    @api.multi
    @api.onchange('asset_id')
    def _onchange_asset_id(self):
        for r in self:
            r.counter_type_id = self.env['asset.consumption.counter.type']
            counter = r.asset_id.counter_type_ids
            domain = {'domain':{'counter_type_id':[('id', 'in', counter.ids)]}}
            return domain

    """
    @api.constrains('quantity')
    def eval_quantity(self):
        for line in self:
            line_counter = line.asset_id \
                .mapped('asset_consumption_line_ids') \
                .filtered(
                    lambda x: x.counter_type_id == self.counter_type_id
                        and x.state in ('adjusted', 'invoiced')
                )

            if line.quantity < max(line_counter.mapped(quantity)):
                    raise UserError(_(
                        "Quantity can't be lower than the last one registered"
                    ))
    """

class AssetConsumptionCounterType(models.Model):
    _name = 'asset.consumption.counter.type'
    _description = 'Asset Consumption Counter Type'

    name = fields.Char(string="name", )

    asset_ids = fields.Many2many(
        'account.asset.asset',
        'counter_type_asset_rel',
        'counter_type_ids',
        'asset_ids',
        string="Asset's",
         )

    _sql_constraints = [
    ('name_unique', 'UNIQUE(name)',  'Error: Name must be unique!')]


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    asset_consumption_line_ids = fields.One2many(
        'account.asset.asset.consumption',
        'asset_id',
        string='Asset consumptions',
    )

    analytic_line_ids = fields.Many2many(
        'account.analytic.invoice.line',
        'asset_analytic_line_rel',
        'asset_ids',
        'analytic_line_ids',
        string='Consumption lines',
         )

    contract_ids = fields.One2many(
        'account.analytic.account',
        string='Contract',
        compute='_get_contract_ids'
    )
    counter_type_ids = fields.Many2many(
        'asset.consumption.counter.type',
        'counter_type_asset_rel',
        'asset_ids',
        'counter_type_ids',
        string='Counter types', )


    @api.depends('analytic_line_ids')
    def _get_contract_ids(self):
        contracts = self.analytic_line_ids.mapped('analytic_account_id')
        self.contract_ids = contracts
