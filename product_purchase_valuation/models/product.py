# -*- coding: utf-8 -*-

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp


class ProductProduct(models.Model):
    _inherit = 'product.product'

    invoice_line_ids = fields.One2many(
        'account.invoice.line',
        'product_id',
        domain=[('invoice_id.type', '=', 'in_invoice'), ('invoice_id.state','in',('open','paid'))],
        string='Invoice lines',
    )

    @api.multi
    def get_product_valuation(self):
        for r in self:
            # Calcular la cantidad del inventario inicial.
            qty = 0.00
            valuation = 0.00
            invoice_lines = r.invoice_line_ids
            invoice_lines = invoice_lines.sorted(lambda x: x.invoice_id.date_invoice)
            inventory_valuation = valuation * qty
            for il in invoice_lines:
                # ¿Debemos calcular en base al inventario a la fecha?
                il_qty = r.uom_id._compute_qty(il.uom_id.id, il.quantity, r.uom_id.id)
                qty += il_qty
                inventory_valuation += il.price_subtotal
                valuation = inventory_valuation / qty
                il.write({
                    'date_valuation': il.invoice_id.date_invoice,
                    'product_valuation': valuation,
                })


"""
class ProductTemplate(models.Model):
    _inherit = 'product.product'

    invoice_line_ids = fields.One2many(
        'account.invoice.line',
        'product_id',
        domain=[('invoice_id.type', '=', 'in_invoice'), ('state','in',('open','paid'))],
        string='Invoice lines',
        )
"""
