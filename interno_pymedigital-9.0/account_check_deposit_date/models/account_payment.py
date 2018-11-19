# -*- coding: utf-8 -*-
###############################################################################
#
#   @author: Daniel Alejandro Mendieta <damendieta@fslibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#
###############################################################################
from openerp import models, fields, api, _


class AccountPayment(models.Model):
    _inherit = "account.payment"

    date_deposit = fields.Date(string="Deposit date", )


class AccountRegisterPayments(models.TransientModel):
    _inherit = "account.register.payments"

    date_deposit = fields.Date(string="Deposit date", )

    @api.model
    def get_payment_vals(self):
        res = super(AccountRegisterPayments, self).get_payment_vals()
        res.update({'date_deposit': self.date_deposit,})
        return res

