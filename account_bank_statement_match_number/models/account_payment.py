# -*- coding: utf-8 -*-
####################################################
# Licencia AGPL-v3                                 #
####################################################
from openerp import api, fields, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    bank_match_number = fields.Char(string="Referencia bancaria", )


class AccountRegisterPayments(models.TransientModel):
    _inherit = 'account.register.payments'

    bank_match_number = fields.Char(string="Referencia bancaria", )

    #def get_payment_batch_vals(self, inv_payment=False, group_data=None):
    #    res = super(AccountRegisterPayments, self).get_payment_batch_vals(inv_payment, group_data)
    #    if self.bank_match_number:
    #        res['bank_match_number'] = self.bank_match_number
    #    return res

    def get_payment_vals(self):
        res = super(AccountRegisterPayments, self).get_payment_vals()

        if self.bank_match_number:
            res['bank_match_number']=self.bank_match_number
        return res
