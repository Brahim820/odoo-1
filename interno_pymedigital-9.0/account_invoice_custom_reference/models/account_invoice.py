# -*- coding: utf-8 -*-

from openerp import api, fields, models


class AccountInvoiceReference(models.Model):
    _name = 'account.invoice.reference'
    _description = 'Account Invoice Reference'

    name = fields.Char(string='Name', )


class AccountInvoice(models.Model):
    _inherit = ['account.invoice']

    reference_id = fields.Many2one('account.invoice.reference', string='Reference type', readonly=True,
                                  states={'draft': [('readonly', False)]})

    @api.onchange('reference_id')
    def _onchange_reference_id(self):
        for r in self:
            r.reference = r._get_reference()
        return


    @api.multi
    def _get_reference(self):
        for r in self:
            if not r.reference_id:
                return
            return r.reference_id.name

