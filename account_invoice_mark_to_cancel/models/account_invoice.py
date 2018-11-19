# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import fields, models, api, _
from openerp import exceptions
from datetime import datetime


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    state = fields.Selection(selection_add=[('to_cancel', 'To cancel')])

    @api.multi
    def button_mark_to_cancel(self):
        for inv in self:
            inv.state = 'to_cancel'
