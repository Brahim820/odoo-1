# -*- coding: utf-8 -*-
import base64
from cStringIO import StringIO

import logging
_logger = logging.getLogger(__name__)

from openerp import models, fields, api, _
from openerp.exceptions import UserError

try:
    import openpyxl
except ImportError:
    _logger.error("The module openpyxl can't be loaded, try: pip install openpyxl")

class BiPurchaceReport(models.TransientModel):
    _name = 'bi.purchase.report'
    _inherit = 'bi.abstract.report'
    _description = 'Bi Purchace Report'

    type = fields.Selection([
            ('purchaces','Purchaces'),
            ('purchace_lines','Purchace lines'),
        ], default="purchaces",
        string='Type',
    )

    local = fields.Boolean(string='Local', default=True, )
    foreign = fields.Boolean(string='Foreing', default=True, )

    group_by = fields.Selection([
            ('salesperson','Salesperson'),
            ('partner','Partner'),
            ('none','None'),
        ], default="none",
        string='Group by',
        )

    user_ids = fields.Many2many(
        'res.users',
        'user_report_rel',
        'report_ids',
        'user_ids',
        string='Salesperson', )

    partner_ids = fields.Many2many(
        'res.partner',
        'partner_report_rel',
        'report_ids',
        'partner_ids',
        string='Partners', )

    def get_purchace_vals(self, i):
        vals = [
            i.number,
            i.partner_id.name,
            i.secuencial,
            i.date_purchace,
            i.date_due,
            (fields.Date.from_string(i.date_due) - fields.Date.from_string(fields.Date.today())).days,
            i.total,
            i.total - i.residual,
            i.residual,
            i.user_id.name,
        ]
        return vals

    def get_purchace_header(self):
        return [
            _(u'FACTURA'),
            _(u'CLIENTE'),
            _(u'SECUENCIAL'),
            _(u'FECHA EMISIÓN'),
            _(u'FECHA VENCIMIENTO'),
            _(u'DIAS'),
            _(u'VALOR TOTAL'),
            _(u'VALOR PAGADO'),
            _(u'VALOR PENDIENTE'),
            _(u'VENDEDOR'),
            ]

    def get_purchace_line_header(self):
        return [
            _(u'TIPO FACTURA'),
            _(u'REGISTRO'),
            _(u'SECUENCIAL'),
            _(u'CLIENTE'),
            _(u'RUC CLIENTE'),
            _(u'PAÍS'),
            _(u'PROVINCIA'),
            _(u'FECHA EMISIÓN'),
            _(u'AÑO EMISIÓN'),
            _(u'MES EMISIÓN'),
            _(u'VENDEDOR'),
            _(u'CÓDIGO PRODUCTO'),
            _(u'TIPO DE PRODUCTO'),
            _(u'CATEGORÍA DE PRODUCTO'),
            _(u'PRODUCTO'),
            _(u'CANTIDAD'),
            _(u'UOM'),
            _(u'PRECIO UNITARIO'),
            _(u'DESCUENTO'),
            _(u'SUBTOTAL SIN IMPUESTOS'),
            _(u'IVA'),
            _(u'TOTAL'),



    def get_purchace_line_vals(self, l):
        inv = l.purchace_id
        pa = inv.partner_id
        pr = l.product_id
        tax_lines = l.sri_tax_line_ids.filtered(
            lambda x: x.group in ('ImpGrav'))

        iva = 0
        if tax_lines:
            iva = sum(tax_lines.mapped('amount'))
        vals = [
            inv.type,
            inv.number,
            inv.secuencial,
            pa.name,
            pa.vat,
            pa.country_id.name,
            pa.state_id.name,
            inv.date_purchace,
            inv.date_purchace[:4],
            inv.date_purchace[5:7],
            inv.user_id.name,
            pr.default_code,
            pr.default_code and pr.default_code[:2] or '',
            pr.categ_id.name,
            pr.name,
            l.quantity,
            l.uom_id.name,
            l.price_unit,
            l.price_discount,
            l.price_subtotal,
            iva,
            l.price_subtotal + iva
        ]
        return vals

    def get_purchace_report_sheet(self, sheetname, rows, inv):
        if self.type == 'purchaces':
            for i in inv:
                vals = self.get_purchace_vals(i)
                rows.append(vals)

        elif self.type == 'purchace_lines':
            lines = inv.mapped('purchace_line_ids')
            for l in lines:
                vals = self.get_purchace_line_vals(l)
                rows.append(vals)
        return {
            'name': sheetname,
            'rows': rows,
            }

    @api.multi
    def get_report_data(self):

        inv_obj = self.env['purchace.order']

        report_filter = []

        if self.partner_ids:
            report_filter.append(('partner_id', 'in', self.partner_ids.ids))
        if self.date_from:
            report_filter.append(('date_order','>=', self.date_from))
        if self.date_to:
            report_filter.append(('date_order','<=', self.date_to))

        inv = inv_obj.search(report_filter)

        if not self.local:
            inv.filtered(lambda x: x.partner_id.country_id != self.env.user.companty_id.country_id)
        if not self.foreign:
            inv.filtered(lambda x: x.partner_id.country_id == self.env.user.companty_id.country_id)

        inv = inv.sorted(lambda x: (x.user_id, x.partner_id))
        sheets = []
        if self.type == 'purchaces':
            filename = 'reporte_de_facturas.xlsx'
            sheetname = 'Facturas'
            header = self.get_purchace_header()
        elif self.type == 'purchace_lines':
            filename = 'reporte_de_facturas_detallado.xlsx'
            sheetname = 'Detalle de facturas'
            header = self.get_purchace_line_header()

        if self.group_by == 'salesperson':
            records = inv.mapped('user_id')
            for r in records:
                sheetname = r.name
                rows = [header]
                r_inv = inv.filtered(lambda x: x.user_id == r)
                sheet = self.get_purchace_report_sheet(sheetname, rows, r_inv)
                sheets.append(sheet)
        elif self.group_by == 'partner':
            records = inv.mapped('partner_id')
            for r in records:
                sheetname = r.name
                rows = [header]
                r_inv = inv.filtered(lambda x: x.partner_id == r)
                sheet = self.get_purchace_report_sheet(sheetname, rows, r_inv)
                sheets.append(sheet)
        else:
            rows = [header]
            sheet = self.get_purchace_report_sheet(sheetname, rows, inv)
            sheets.append(sheet)

        data = {
            'wizard': 'bi.purchase.report',
            'filename': filename,
            'sheets': sheets,
        }

        return data

