# -*- coding: utf-8 -*-
####################################################
# Parte del Proyecto LibreGOB: http://libregob.org #
# Licencia AGPL-v3                                 #
####################################################

from openerp import models, fields, api


class CreditCredit(models.Model):
    _inherit = 'credit.credit'


    credit_type_id = fields.Many2one('credit.credit.type', string='Credit type', )
    code = fields.Char(string='Code',related="partner_id.code")
    account_id = fields.Many2one('account.account', string='Account', )


class CreditCreditType(models.Model):
    _name = 'credit.credit.type'
    _description = 'Credit Credit Type'

    name = fields.Char(string="Name", required=True,  )
    priority = fields.Char(string='Priority', required=True,  )




