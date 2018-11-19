# -*- coding: utf-8 -*-
###############################################################################
#
#   @author: Daniel Alejandro Mendieta <damendieta@fslibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#
###############################################################################
from openerp import _, api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    date_deposit = fields.Date(string="Deposit date", )

    @api.model
    def create(self, vals, apply_taxes=True):
        if vals.get('payment_id'):
            payment_id = vals.get('payment_id')
            payment = self.env['account.payment'].browse(payment_id)
            vals['date_deposit'] = payment.date_deposit
        return super(AccountMoveLine, self).create(vals, apply_taxes=apply_taxes)
