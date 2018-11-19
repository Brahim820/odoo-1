# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    purchase_discount_account_id = fields.Many2one(
        'account.account', string='Purchase discount account',
        domain=[('deprecated', '=', False)],
        help="The account related to purchase discounts.", )
    sale_discount_account_id = fields.Many2one(
        'account.account', string='Sale discount account',
        domain=[('deprecated', '=', False)],
        help="The account related to sale discounts.", )
