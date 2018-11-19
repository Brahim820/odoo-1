# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions, _
import openerp.addons.decimal_precision as dp


class PurchaseCompleteFromTemplate(models.TransientModel):
    _name = "purchase.complete.from.template"
    _description = "Complete order from template"

    purchase_template_id = fields.Many2one(
        'purchase.order.template', ondelete='set null',
        string="Purchase template", required=True, )

    purchase_lines = fields.One2many(
        'purchase.complete.from.template.line',
        'wizard_id',
        string='Purchase lines',
    )

    date_planned = fields.Datetime('Planned date', required=True, )
    set_product_qty = fields.Selection(
        [('no', 'No'),
         ('keep', 'Yes and keep the quantity'),
         ('reset', 'Yes and reset the quantity'),
         ],
        default='no',
        string='Include quantity', )
    partner_id = fields.Many2one(
        'res.partner', ondelete='set null', string="Vendor",
        domain="[('supplier','=', True)]", required=True, )
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Picking type', required=True,
        domain=[('code', '=', 'incoming')], )

    @api.onchange('purchase_template_id')
    def onchange_purchase_template_id(self):
        self.partner_id = self.purchase_template_id.partner_id

    @api.multi
    def complete_from_template(self):
        template = self.purchase_template_id
        for line in template.template_line_ids:
            print 'LINE', line
            product_qty = line.product_qty
            if self.set_product_qty == 'no':
                product_qty = 0.0
            if self.set_product_qty == 'reset':
                line.write({'product_qty': 0.0 })

            self.purchase_lines.create({
                'product_id': line.product_id.id,
                'product_uom': line.product_uom.id,
                'product_qty': product_qty,
                'wizard_id': self.id,
            })

    @api.multi
    def create_order_lines(self, order=None, line=None, date_planned=None):
        fpos = self.partner_id.property_account_position_id
        taxes_ids = fpos.map_tax(line.product_id.supplier_taxes_id).ids

        seller = line.product_id._select_seller(
            line.product_id,
            partner_id=self.partner_id,
            quantity=line.product_qty,
            date=date_planned[:10],
            uom_id=line.product_uom)

        price_unit = self.env['account.tax']._fix_tax_included_price(seller.price, line.product_id.supplier_taxes_id, taxes_ids) if seller else 0.0

        product_lang = line.product_id.with_context({
            'lang': self.partner_id.lang,
            'partner_id': self.partner_id.id,
        })

        self.env['purchase.order.line'].create({
            'name': product_lang.display_name,
            'order_id': order.id,
            'date_planned': date_planned,
            'product_id': line.product_id.id,
            'price_unit': price_unit,
            'taxes_id': [(6, 0, taxes_ids)],
            'product_qty': line.product_qty,
            'product_uom': line.product_uom.id,
        })

    @api.multi
    def create_order(self):
        date_planned = self.date_planned

        if not date_planned:
            raise exceptions.UserError(_('Select a scheduled date first.'))

        order = self.env['purchase.order'].create({
            'date_order': self.date_planned,
            # 'date_planned': self.date_planned,
            'partner_id': self.partner_id.id,
            'fiscal_position_id': self.partner_id.property_account_position_id.id,
            'picking_type_id': self.picking_type_id.id,
        })

        lines = self.mapped('purchase_lines').filtered(lambda x: x.product_qty != 0)
        for line in lines:
            self.create_order_lines(order=order, line=line, date_planned=date_planned)

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': order.id,
            'target': 'current',
        }


class PurchaseCompleteFromTemplateLine(models.TransientModel):
    _name = "purchase.complete.from.template.line"
    _description = "Complete order from template line"

    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_qty = fields.Float(string='Required Quantity', digits_compute=dp.get_precision('Product Unit of Measure'), required=True)
    product_uom = fields.Many2one('product.uom', 'UoM', required=True)
    wizard_id = fields.Many2one('purchase.complete.from.template', string='Wizard', )