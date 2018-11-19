# -*- encoding: utf-8 -*-
from openerp import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    tuition_ok = fields.Boolean("Pensión", )

    @api.multi
    @api.onchange('tuition_ok')
    def onchange_tuition_ok(self):
        for r in self:
            if r.tuition_ok:
                r.type = 'service'
