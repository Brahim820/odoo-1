# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class ResCompany(models.Model):
    _inherit = "res.company"

    account_code_structure = fields.Char(
        string='Code structure',
        default="3.2.2.2.2.2.2.3",
    )

