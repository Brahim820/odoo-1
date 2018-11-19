# -*- coding: utf-8 -*-
import logging

from openerp import _, api, fields, models

_logger = logging.getLogger(__name__)


class BiInvoiceReport(models.TransientModel):
    _name = 'bi.invoice.report'
    _inherit = 'bi.abstract.report'
    _description = 'Bi Invoice Report'

    type = fields.Selection([
        ('invoices', 'Invoices'),
        ('invoice_lines', 'Invoice lines'),
    ], default="invoices",
        string='Type',
    )

    local = fields.Boolean(string='Local', default=True, )
    foreign = fields.Boolean(string='Foreing', default=True, )

    service = fields.Boolean(string='Service', )
    product = fields.Boolean(string='Product', )
    consu = fields.Boolean(string='Consumable', )

    group_by = fields.Selection([
        ('user', 'User'),
        ('partner', 'Partner'),
        ('none', 'None'),
    ], default="none",
        string='Group by',
    )

    user_ids = fields.Many2many(
        'res.users',
        'user_report_rel',
        'report_ids',
        'user_ids',
        string='User', )

    partner_ids = fields.Many2many(
        'res.partner',
        'partner_report_rel',
        'report_ids',
        'partner_ids',
        string='Partners', )

    in_invoice = fields.Boolean(string='In invoice', )
    out_invoice = fields.Boolean(
        string='Out invoice', default=lambda x: x._context.get('sales', False))
    in_refund = fields.Boolean(string='In refund', )
    out_refund = fields.Boolean(
        string='Out refund', default=lambda x: x._context.get('sales', False))

    def get_invoice_vals(self, i):
        try:
            days = (fields.Date.from_string(i.date_due) -
                    fields.Date.from_string(fields.Date.today())).days
        except TypeError:
            days = 0
        vals = [
            i.number,
            'SI' if i.secretencion1 else 'NO',
            i.origin,
            i.partner_id.name,
            i.secuencial,
            i.date_invoice,
            i.date_due,
            days,
            i.total,
            i.total - i.residual,
            i.residual,
            i.partner_id.user_id.name,
        ]
        return vals

    def get_invoice_header(self):
        return [
            _(u'FACTURA'),
            _(u'RETENCION'),
            _(u'ORIGEN'),
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

    def get_invoice_line_header(self):
        return [
            _(u'TIPO FACTURA'),
            _(u'REGISTRO'),
            _(u'ORIGEN'),
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
            _(u'DETALLE'),
            _(u'CANTIDAD'),
            _(u'UOM'),
            _(u'PRECIO UNITARIO'),
            _(u'DESCUENTO'),
            _(u'SUBTOTAL SIN IMPUESTOS'),
            _(u'IVA'),
            _(u'TOTAL'),
        ]

    def get_invoice_line_vals(self, l):
        inv = l.invoice_id
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
            inv.origin or '',
            inv.secuencial or '',
            pa.name,
            pa.vat,
            pa.country_id.name or '',
            pa.state_id.name or '',
            inv.date_invoice,
            inv.date_invoice[:4],
            inv.date_invoice[5:7],
            inv.user_id.name,
            pr.default_code or '',
            pr.default_code and pr.default_code[:2] or '',
            pr.categ_id.name or '',
            pr.name or l.name,
            l.quantity,
            l.uom_id.name or '',
            l.price_unit,
            l.price_discount,
            l.price_subtotal,
            iva,
            l.price_subtotal + iva
        ]
        return vals

    def get_invoice_report_sheet(self, sheetname, rows, inv):
        if self.type == 'invoices':
            for i in inv:
                vals = self.get_invoice_vals(i)
                rows.append(vals)

        elif self.type == 'invoice_lines':
            lines = inv.mapped('invoice_line_ids')
            product_types = []
            if self.consu:
                product_types.append('consu')
            if self.product:
                product_types.append('product')
            if self.service:
                product_types.append('service')
            if product_types:
                lines.filtered(lambda x: x.product_id.type in product_types)

            for l in lines:
                vals = self.get_invoice_line_vals(l)
                rows.append(vals)
        return {
            'name': sheetname,
            'rows': rows,
        }

    @api.multi
    def get_report_data(self):

        inv_obj = self.env['account.invoice']

        report_filter = []
        types = []

        if self.out_invoice:
            types.append('out_invoice')
        if self.in_invoice:
            types.append('in_invoice')
        if self.out_refund:
            types.append('out_refund')
        if self.in_refund:
            types.append('in_refund')

        report_filter.append(('type', 'in', types))

        if self.partner_ids:
            report_filter.append(('partner_id', 'in', self.partner_ids.ids))
        if self.date_from:
            report_filter.append(('date_invoice', '>=', self.date_from))
        if self.date_to:
            report_filter.append(('date_invoice', '<=', self.date_to))
        report_filter.append(('state', 'not in', ['draft', 'cancel']))
        inv = inv_obj.search(report_filter)

        if not self.local:
            inv.filtered(lambda x: x.partner_id.country_id != self.env.user.companty_id.country_id)
        if not self.foreign:
            inv.filtered(lambda x: x.partner_id.country_id == self.env.user.companty_id.country_id)

        inv = inv.sorted(lambda x: (x.user_id, x.partner_id))
        sheets = []
        if self.type == 'invoices':
            filename = 'reporte_de_facturas.xlsx'
            sheetname = 'Facturas'
            header = self.get_invoice_header()
        elif self.type == 'invoice_lines':
            filename = 'reporte_de_facturas_detallado.xlsx'
            sheetname = 'Detalle de facturas'
            header = self.get_invoice_line_header()

        if self.group_by == 'user':
            records = inv.mapped('user_id')
            for r in records:
                sheetname = r.name
                rows = [header]
                r_inv = inv.filtered(lambda x: x.user_id == r)
                sheet = self.get_invoice_report_sheet(sheetname, rows, r_inv)
                sheets.append(sheet)
        elif self.group_by == 'partner':
            records = inv.mapped('partner_id')
            for r in records:
                sheetname = r.name
                rows = [header]
                r_inv = inv.filtered(lambda x: x.partner_id == r)
                sheet = self.get_invoice_report_sheet(sheetname, rows, r_inv)
                sheets.append(sheet)
        else:
            rows = [header]
            sheet = self.get_invoice_report_sheet(sheetname, rows, inv)
            sheets.append(sheet)

        data = {
            'wizard': 'bi.invoice.report',
            'filename': filename,
            'sheets': sheets,
        }

        return data
