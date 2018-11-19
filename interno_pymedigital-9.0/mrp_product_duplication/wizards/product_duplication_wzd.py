# -*- coding: utf-8 -*-

from openerp import _, api, fields, models

class ProductDuplicationWzd(models.TransientModel):
    _name = 'product.duplication.wzd'
    _description = 'Product Duplication Wizard'

    name = fields.Char(default='Product Duplicated')
    company_id = fields.Many2one(comodel_name='res.company', string='Company')

    # bom_qty = fields.Float(string='Qty to produce')
    type = fields.Char(string='Type')
    default_code = fields.Char(string='Internal Reference')

    list_price = fields.Float(string='Sale Price')
    uom_id = fields.Many2one(comodel_name='product.uom', string='Unit of Measure')

    sale_ok = fields.Boolean(string="Can be Sold")
    can_be_expensed = fields.Boolean(string="Can be expensed")
    purchase_ok = fields.Boolean(string="Can be purchased")

    product_variant_count = fields.Integer(string='# of Product Variants', compute="_get_product_variant_count")

    taxes_id = fields.Many2many('account.tax', 'wzd_product_taxes_rel', 'prod_id', 'tax_id', string='Customer Taxes',
        domain=[('type_tax_use', '=', 'sale')])
    supplier_taxes_id = fields.Many2many('account.tax', 'wzd_product_supplier_taxes_rel', 'prod_id', 'tax_id', string='Vendor Taxes',
        domain=[('type_tax_use', '=', 'purchase')])
    property_account_income_id = fields.Many2one('account.account', company_dependent=True,
        string="Income Account", oldname="property_account_income",
        domain=[('deprecated', '=', False)],
        help="This account will be used for invoices instead of the default one to value sales for the current product.")
    property_account_expense_id = fields.Many2one('account.account', company_dependent=True,
        string="Expense Account", oldname="property_account_expense",
        domain=[('deprecated', '=', False)],
        help="This account will be used for invoices instead of the default one to value expenses for the current product.")

    attribute_line_ids = fields.One2many(comodel_name="product.duplication.wzd.line", inverse_name="product_tmpl_id", string="Product Attributes")

    wzd_bom_ids = fields.One2many(comodel_name="product.duplication.wzd.bom", inverse_name="product_duplication_wzd_id", string="Bill of Materials")

    categ_id = fields.Many2one(comodel_name='product.category', string='Internal Category', required=True,
                                domain="[('type','=','normal')]", help="Select category for the current product")
    wzd_route_ids = fields.Many2many("stock.location.route", "wzd_stock_route_product", "product_id", "route_id",
                                     string='Routes', domain=[('product_selectable', '=', True)])

    @api.multi
    @api.depends('attribute_line_ids')
    def _get_product_variant_count(self):
        self.ensure_one()
        self.product_variant_count = sum([len(line.value_ids) for line in self.attribute_line_ids])

    @api.multi
    def action_duplicate_product(self):
        self.ensure_one()

        vals = {
            'name': self.name,
            'company_id': self.company_id and self.company_id.id or False,
            'type': self.type,
            'default_code': self.default_code,
            'list_price': self.list_price,
            'uom_id': self.uom_id.id,
            'sale_ok': self.sale_ok,
            'can_be_expensed': self.can_be_expensed,
            'purchase_ok': self.purchase_ok,
            'property_account_income_id': self.property_account_income_id and self.property_account_income_id.id or False,
            'property_account_expense_id': self.property_account_expense_id and self.property_account_expense_id.id or False,
            'attribute_line_ids' : [],
            'categ_id': self.categ_id and self.categ_id.id or False,
        }
        for attr_line in self.attribute_line_ids:
            line = {
                'attribute_id': attr_line.attribute_id.id,
                'value_ids': attr_line.value_ids and [[6, False, [at.id for at in attr_line.value_ids]]] or False
            }
            vals['attribute_line_ids'].append([0, False, line])

        vals['route_ids'] = self.wzd_route_ids and [[6, False, [t.id for t in self.wzd_route_ids]]] or False

        vals['taxes_id'] = self.taxes_id and [[6, False, [t.id for t in self.taxes_id]]] or False
        vals['supplier_taxes_id'] = self.supplier_taxes_id and [[6, False, [t.id for t in self.supplier_taxes_id]]] or False

        product_template_id = self.env['product.template'].create(vals)
        if product_template_id:
            for bom in self.wzd_bom_ids:
                new_bom = {
                    'product_tmpl_id': product_template_id.id,
                    'code': bom.code,
                    'type': bom.type,
                    'product_qty': bom.product_qty,
                    'product_uom': bom.product_uom.id,
                    'product_efficiency': bom.product_efficiency,
                    'company_id': bom.company_id.id,
                    'bom_line_ids': bom.bom_line_ids and [
                                        [0, False, {
                                            'product_id': line.product_id.id,
                                            'product_qty': line.product_qty,
                                            'product_uom': line.product_uom.id
                                        }] for line in bom.bom_line_ids]
                                    or False
                }
                self.env['mrp.bom'].create(new_bom)

            view_id = self.env['ir.model.data'].get_object_reference(
                'product',
                'product_template_only_form_view')[1]

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'product.template',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view_id,
                'res_id': product_template_id.id,
            }

        return True


class ProductDuplicationWzdLine(models.TransientModel):
    _name = 'product.duplication.wzd.line'

    product_tmpl_id = fields.Many2one(comodel_name="product.duplication.wzd", string="Product Template", required=True, )
    attribute_id = fields.Many2one(comodel_name="product.attribute", string="Attribute", required=True, )
    value_ids = fields.Many2many(comodel_name="product.attribute.value", column1="line_id", column2="val_id", string="Attribute Values", )


class ProductDuplicationWzdBOM(models.TransientModel):
    _name = 'product.duplication.wzd.bom'
    _rec_name = "code"

    code = fields.Char(string="Code", required=False, )
    type = fields.Selection(selection=[('normal','Manufacture this product'),('phantom','Ship this product as a set of components (kit)')],
                            string="Type", required=True, )

    product_duplication_wzd_id = fields.Many2one(comodel_name="product.duplication.wzd", string="Product Template",)
    product_qty = fields.Float('Product Quantity')
    product_uom = fields.Many2one(comodel_name='product.uom', string='Product Unit of Measure', required=True)
    bom_line_ids = fields.One2many(comodel_name="product.duplication.wzd.bom.line", inverse_name="bom_id", string="Lines")

    product_efficiency = fields.Float(string="Manufacturing Efficiency",  required=True,
                                      default=1.0)
    company_id = fields.Many2one(comodel_name='res.company', string='Company', required=True,
                                 default=lambda self: self.env['res.company']._company_default_get('mrp.bom'))

class WzdBOMLine(models.TransientModel):
    _name = 'product.duplication.wzd.bom.line'
    _rec_name = "bom_id"

    bom_id = fields.Many2one(comodel_name="product.duplication.wzd.bom", string="Bom" )

    product_id = fields.Many2one(comodel_name='product.product', string='Product', required=True)
    product_qty = fields.Float(string='Product Quantity', required=True)
    product_uom = fields.Many2one(comodel_name='product.uom', string='Product Unit of Measure', required=True)


    @api.onchange('product_id')
    def _onchange(self):
        self.product_uom = self.product_id and self.product_id.uom_id and self.product_id.uom_id.id or False
