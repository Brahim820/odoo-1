# -*- coding: utf-8 -*-
####################################################
# Licencia AGPL-v3                                 #
####################################################

from openerp import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.multi
    def get_all_bank_match_numbers(self):
        for r in self:
            move_line_obj = self.env['account.move.line']
            moves = move_line_obj.search([])
            moves.get_bank_match_number()

    @api.multi
    def get_bank_match_number(self):
        for r in self:
            if r.payment_id:
                p = r.payment_id
                r.bank_match_number = p.check_number or p.bank_match_number

    @api.model
    def create(self, vals, apply_taxes=True):
        res = super(AccountMoveLine, self).create(
            vals, apply_taxes=apply_taxes)
        res.get_bank_match_number()
        return res

    bank_match_number = fields.Char(
        string="Referencia bancaria", default="get_bank_match_number", )

