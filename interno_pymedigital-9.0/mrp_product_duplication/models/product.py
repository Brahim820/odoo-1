# -*- coding: utf-8 -*-

from openerp import models, api, fields, _

class product_template(models.Model):
    _inherit = "product.template"

    @api.multi
    def button_duplicate(self):
        self.ensure_one()

        view_id = self.env['ir.model.data'].get_object_reference(
            'mrp_product_duplication',
            'product_duplication_wzd_view')[1]

        lista_variantes = self.attribute_line_ids and [
            [0, False, {
                'attribute_id': v.attribute_id.id, 
                'value_ids': v.value_ids.ids
            }] for v in self.attribute_line_ids] or False
        
        context = {
            'default_name': self.name,
            'default_company_id': self.company_id.id,
            'default_type': self.type,
            'default_default_code': self.default_code,
            'default_list_price': self.list_price,
            # 'default_standard_price': self.standard_price,
            'default_barcode': self.barcode,
            'default_uom_id': self.uom_id.id,

            'default_sale_ok': self.sale_ok,
            'default_can_be_expensed': self.can_be_expensed,
            'default_purchase_ok': self.purchase_ok,

            'default_taxes_id': self.taxes_id.ids,
            'default_supplier_taxes_id': self.supplier_taxes_id.ids,
            'default_property_account_income_id': self.property_account_income_id.id,
            'default_property_account_expense_id': self.property_account_expense_id.id,

            'default_attribute_line_ids': lista_variantes,
            'default_wzd_bom_ids': self._get_bom_list().ids,

            'default_categ_id': self.categ_id and self.categ_id.id or False,
            'default_wzd_route_ids': self.route_ids.ids,#self.route_ids and [[6, False, [it.id for it in self.route_ids]]] or False,
        }

        return {
            'name': _('Duplicate product'),
            'type': 'ir.actions.act_window',
            'res_model': 'product.duplication.wzd',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': context
        }

    @api.multi
    def _get_bom_list(self):
        self.ensure_one()
        bom_list = self.env['product.duplication.wzd.bom']

        for bom in self.env['mrp.bom'].search([('product_tmpl_id', '=', self.id)]):
            line_ids = [[0, False, {
                'product_id': line.product_id.id,
                'product_qty': line.product_qty,
                'product_uom': line.product_uom.id,
            }] for line in bom.bom_line_ids]

            wzd_bom = self.env['product.duplication.wzd.bom'].create({'code': bom.code,
                             'type': bom.type,
                             'product_qty': bom.product_qty,
                             'product_uom': bom.product_uom.id,
                             'product_efficiency': bom.product_efficiency,
                             'company_id': bom.company_id.id,
                             'bom_line_ids': line_ids
                             })

            bom_list += wzd_bom

        return bom_list
