# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions, _
import openerp.addons.decimal_precision as dp


class PurchaseOrderTemplateLine(models.Model):
    _name = 'purchase.order.template.line'

    @api.multi
    @api.onchange('product_id')
    def _onchange_uom_domain(self):
        for r in self:
            uom_category = r.product_id.uom_id.category_id.id
            r.product_uom = r.product_id.uom_id
            return {'domain':{'product_uom': [('category_id', '=', uom_category)]}}

    product_id = fields.Many2one(
        'product.product', ondelete='set null', string="Product",
        required=True, )
    product_uom = fields.Many2one(
        'product.uom', ondelete='set null', string="Product UOM", )
    product_qty = fields.Float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure'), )
    template_id = fields.Many2one('purchase.order.template', string='Template', ondelete='cascade', )


class PurchaseOrderTemplate(models.Model):
    _name = 'purchase.order.template'

    partner_id = fields.Many2one(
        'res.partner', ondelete='set null', string="Vendor",
        domain="[('supplier','=', True)]", )

    name = fields.Char('Name', )
    template_line_ids = fields.One2many(
        'purchase.order.template.line', 'template_id', string='Template lines', )

