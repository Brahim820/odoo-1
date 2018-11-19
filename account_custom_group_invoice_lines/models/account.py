# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import  models, fields 


class AccountJournal(models.Model):
    _inherit = "account.journal"
    
    group_by_account_id = fields.Boolean(string='Group by account', default=True,)
    group_by_tax_ids = fields.Boolean(string='Group by taxes', default=True,)
    group_by_tax_line_id = fields.Boolean(string='Group by tax lines', default=True,)
    group_by_product_id = fields.Boolean(string='Group by product', default=False,)
    group_by_analytic_account_id = fields.Boolean(string='Group by analitic account', default=True,)
    group_by_date_maturity = fields.Boolean(string='Group by date maturity', default=True,)
