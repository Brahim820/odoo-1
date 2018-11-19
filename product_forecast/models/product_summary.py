# -*- coding: utf-8 -*-

from openerp import fields, models, tools


class ViewProductSummary(models.Model):
    """View Product Summary"""
    _name = 'view.product.summary'
    _order = 'year, month desc'
    _auto = False

    product_id = fields.Many2one('product.product', 'Product')
    code = fields.Char('Code')
    name = fields.Char('Name')
    origin = fields.Char('Origin')
    doc_uom = fields.Many2one('product.uom', 'Doc Origin UOM')
    uom_id = fields.Many2one('product.uom', 'Product UOM')
    doc_date = fields.Date('Date of Consumption')
    year = fields.Integer('Year')
    month = fields.Integer('Month')
    date = fields.Date('Date')
    type = fields.Char('Type')
    qty = fields.Float('Quantity')
    price = fields.Float('Price')

    def init(self, cr):
        """Initialize SQL View"""
        tools.drop_view_if_exists(cr, 'view_product_summary')

        cr.execute("""CREATE VIEW view_product_summary AS (
SELECT (l.id::character varying::text || 'I'::text) || COALESCE(l.id::character varying, ''::character varying)::text AS id,
    l.product_id,
    p.default_code AS code,
    t.name,
    i.number AS origin,
    l.uom_id AS doc_uom_id,
    u.id AS uom_id,
    i.date_invoice AS doc_date,
    to_char(i.date_invoice::timestamp with time zone, 'YYYY'::text)::integer AS year,
    to_char(i.date_invoice::timestamp with time zone, 'MM'::text)::integer AS month,
    i.type AS doc_type,
    l.quantity AS qty,
    l.price_subtotal AS price
   FROM account_invoice_line l
     JOIN account_invoice i ON l.invoice_id = i.id
     JOIN product_product p ON p.id = l.product_id
     JOIN product_template t ON p.product_tmpl_id = t.id
     JOIN product_uom u ON t.uom_id = u.id
  WHERE (l.invoice_id IN ( SELECT account_invoice.id
           FROM account_invoice
          WHERE account_invoice.state::text = ANY (ARRAY['open'::character varying::text, 'paid'::character varying::text]))) AND t.active IS TRUE
UNION ALL
 SELECT (s.id::character varying::text || 'S'::text) || COALESCE(s.id::character varying, ''::character varying)::text AS id,
    s.product_id,
    p.default_code AS code,
    t.name,
    m.name AS origin,
    s.product_uom AS doc_uom_id,
    t.uom_id,
    s.date AS doc_date,
    to_char(s.date, 'YYYY'::text)::integer AS year,
    to_char(s.date, 'MM'::text)::integer AS month,
    'mrp_consumption'::character varying AS doc_type,
    s.product_qty AS qty,
    0 AS price
   FROM stock_move s
     JOIN mrp_production m ON m.id = s.raw_material_production_id
     JOIN product_product p ON s.product_id = p.id
     JOIN product_uom u ON m.product_uom = u.id
     JOIN product_template t ON t.id = p.product_tmpl_id
  WHERE s.state::text = 'done'::text AND t.active IS TRUE

UNION ALL
 SELECT (s.id::character varying::text || 'P'::text) || COALESCE(s.id::character varying, ''::character varying)::text AS id,
    s.product_id,
    p.default_code AS code,
    t.name,
    m.name AS origin,
    s.product_uom AS doc_uom_id,
    t.uom_id,
    s.date AS doc_date,
    to_char(s.date, 'YYYY'::text)::integer AS year,
    to_char(s.date, 'MM'::text)::integer AS month,
    'mrp_production'::character varying AS doc_type,
    s.product_qty AS qty,
    0 AS price
   FROM stock_move s
     JOIN mrp_production m ON m.id = s.production_id
     JOIN product_product p ON s.product_id = p.id
     JOIN product_uom u ON m.product_uom = u.id
     JOIN product_template t ON t.id = p.product_tmpl_id
  WHERE s.state::text = 'done'::text AND t.active IS TRUE
)""")
