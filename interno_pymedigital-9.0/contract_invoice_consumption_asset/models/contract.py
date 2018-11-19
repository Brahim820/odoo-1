# -*- coding: utf-8 -*-
####################################################
# Parte del Proyecto LibreGOB: http://libregob.org #
# Licencia AGPL-v3                                 #
####################################################

from openerp import models, fields, api, _
from openerp.exceptions import UserError, ValidationError


class AccountAnalyticInvoiceLine(models.Model):
    _inherit = 'account.analytic.invoice.line'

    asset_ids = fields.Many2many(
        'account.asset.asset',
        'asset_analytic_line_rel',
        'analytic_line_ids',
        'asset_ids',
        string='Assets',
        required=True, )

    counter_type_id = fields.Many2one('asset.consumption.counter.type',
        string='Counter type')

    qty_formula_id = fields.Many2one('contract.line.qty.formula',
        string="Qty. formula",
        default=1,  )

    @api.multi
    @api.onchange('asset_ids')
    def _onchange_asset_ids(self):
        for r in self:
            r.counter_type_id = self.env['asset.consumption.counter.type']
            if not r.asset_ids:
                return {'domain':{
                    'counter_type_id':[('id', 'in', [])]}
                }
            counter = r.asset_ids.mapped('counter_type_ids')
            domain = {'domain':{'counter_type_id':[('id', 'in', counter.ids)]}}
            return domain


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.model
    def _prepare_invoice_line(self, line, invoice_id):
        if line.qty_type != 'variable':
            res = super(AccountAnalyticAccount, self) \
            ._prepare_invoice_line(line, invoice_id)
            res.update(
            {'name': '{}'.format(line.name) + '\n' +
                    ', '.join(line.asset_ids.mapped('name')),
            'analytic_account_id': line.analytic_account_id.id,
            }
            )
            return res

        asset_start_qty = 0
        asset_final_qty = 0
        start_qty = 0
        final_qty = 0
        name = _('Counter') + unicode(line.counter_type_id.name) + '\n'
        consumption_lines = self.env['account.asset.asset.consumption']
        assets = line.asset_ids
        for asset in assets:
            name += unicode(asset.name + ':\n'   )
            lines_counter = asset.mapped('asset_consumption_line_ids') \
                .filtered(
                    lambda x: x.counter_type_id == line.counter_type_id
                )
            lines_inv_adj = lines_counter \
                .filtered(lambda x: x.state == 'invoiced'
                        or x.state == 'adjusted')

            lines_confirmed = lines_counter \
                .filtered(lambda x: x.state == 'confirmed')


            if lines_inv_adj:
                inv_adj_quants = lines_inv_adj.mapped('quantity')
                asset_start_qty = max(inv_adj_quants)
                start_qty += asset_start_qty

            if len(lines_confirmed) != 1:
                raise UserError(_("There should only one confirmed line"))
            else:
                consumption_lines += lines_confirmed
                asset_final_qty = lines_confirmed.quantity
                final_qty += asset_final_qty


            name = name + '- ' + _('Previous:') + ' ' + str(asset_start_qty) \
                + ' ' + _('Actual:') + ' ' + str(asset_final_qty) + '\n'

        line.start_qty = start_qty
        line.final_qty = final_qty

        res = super(AccountAnalyticAccount, self) \
            ._prepare_invoice_line(line, invoice_id)
        res.update(
            {'asset_consumption_line_ids': [(6,0, consumption_lines.ids)],
             'analytic_account_id': line.analytic_account_id.id,
             'name': name,
            }
        )

        consumption_lines.write({'state': 'invoiced'})
        return res

