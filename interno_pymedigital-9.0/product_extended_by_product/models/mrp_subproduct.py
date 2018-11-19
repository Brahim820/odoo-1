# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api


class MrpSubproduct(models.Model):
    _inherit = 'mrp.subproduct'

    price_weight = fields.Integer(string='Price weight (%)', )


