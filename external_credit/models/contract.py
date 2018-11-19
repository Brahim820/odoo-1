# -*- coding: utf-8 -*-
####################################################
# Parte del Proyecto LibreGOB: http://libregob.org #
# Licencia AGPL-v3                                 #
####################################################


from openerp import models, fields, api


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    credit_type_id = fields.Many2one('credit.credit.type', string='Credit type', )


    @api.multi
    def _prepare_invoice(self):
        res = super(AccountAnalyticAccount, self)._prepare_invoice()
        contract = self[:1]
        if not contract.credit_type_id:
            raise ValidationError(
                _("You must first select a Credit type for Contract %s!") %
                contract.name)
        res.update({'credit_type_id': contract.credit_type_id.id})
        return res


