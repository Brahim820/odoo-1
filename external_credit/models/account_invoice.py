# -*- coding: utf-8 -*-
####################################################
# Parte del Proyecto LibreGOB: http://libregob.org #
# Licencia AGPL-v3                                 #
####################################################

from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'


    credit_type_id = fields.Many2one('credit.credit.type', string='Credit type', )






