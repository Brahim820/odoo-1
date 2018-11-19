# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    communication = fields.Char(
        string='Communication', readonly=True,
        states={'draft': [('readonly', False)]}, )

