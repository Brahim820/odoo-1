# -*- coding: utf-8 -*-
from openerp import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _get_custom_email_cc(self):
        res = []
        for r in self:
            try:
                res.extend(r.partner_id.child_ids.filtered(
                    lambda x: x.type == 'invoice').ids)
            except:
                pass
        return res
