# -*- coding: utf-8 -*-
import base64
import logging
from cStringIO import StringIO

from openerp import _, api, fields, models
from openerp.exceptions import UserError

_logger = logging.getLogger(__name__)


try:
    import openpyxl
except ImportError:
    _logger.error("The module openpyxl can't be loaded, try: pip install openpyxl")


class ReportStockLocationKardex(models.TransientModel):
    _name = 'report.stock.location.kardex'

    xlsx_file = fields.Binary('Production', attachment=False, readonly=True, )
    xlsx_filename = fields.Char(string="Production filename", )
    date_from = fields.Datetime(
        string='Date from',
        required=True,
        default=fields.Datetime.now(), )
    date_to = fields.Datetime(
        string='Date to',
        required=True,
        default=fields.Datetime.now(), )

    costing = fields.Boolean(string='Costing', )

    product_id = fields.Many2one('product.product', string='Product', )
    location_ids = fields.Many2many(
        'stock.location',
        'location_wizard_rel',
        'wizard_ids',
        'location_ids',
        string='Location', )

    type = fields.Selection([
        ('by_location', 'By Location'),
        ('consolidated', 'Consolidated'),
    ], default="by_location",
        string='Type',
    )

    @api.multi
    def get_report_data(self):
        locations = self.location_ids or self.env['stock.location'].search(
            [('usage', '=', 'internal')])

        for location in locations:
            location.button_update_kardex()

        kardex = locations.mapped('kardex_ids')
        kardex = kardex.filtered(
            lambda x: x.product_id == self.product_id
        )

        data = {
            'wizard': 'report.stock.location.kardex',
            'filename': 'kardex.xlsx',
        }

        if self.type == 'consolidated':
            sheet = {
                'name': self.product_id.name,
            }
            rows = []
            header = [
                _(u'FECHA'),
                _(u'NOMBRE'),
                _(u'MOVIMIENTO'),
                _(u'UBICACIÓN'),
                _(u'UBICACIÓN DE TRÁNSITO'),
                _(u'UBICACIÓN RELACIONADA'),
                _(u'CANTIDAD ANTERIOR UBICACIÓN'),
                _(u'CANTIDAD ANTERIOR GLOBAL'),
                _(u'ENTRADAS'),
                _(u'SALIDAS'),
                _(u'CANTIDAD FINAL UBICACIÓN'),
                _(u'CANTIDAD FINAL GLOBAL')
            ]

            if self.costing:
                header.extend([
                    _(u'VALORACIÓN ANTERIOR UBICACIÓN'),
                    _(u'VALORACIÓN ANTERIOR GLOBAL'),
                    _(u'INGRESO'),
                    _(u'EGRESO'),
                    _(u'VALORACIÓN FINAL UBICACIÓN'),
                    _(u'VALORACIÓN FINAL GLOBAL')
                ])
            rows.append(header)

            lines = kardex.mapped('kardex_line_ids').filtered(
                lambda x: x.date >= self.date_from
                and x.date <= self.date_to
            )

            # las salidas son primero en la misma fecha.
            lines = lines.sorted(lambda x: (x.date, x.in_qty))

            previous_balance_qty = previous_balance_value = 0.00
            for location in locations:
                line = lines.filtered(lambda x: x.kardex_id.location_id == location)
                if line:
                    line = line[0]
                previous_balance_qty += line.previous_balance_qty
                if self.costing:
                    previous_balance_value += line.previous_balance_value

            sheets = []
            for l in lines:
                balance_qty = previous_balance_qty + l.in_qty - l.out_qty
                vals = [
                    l.date,
                    l.name,
                    l.picking_id.name_get()[0][1] if l.picking_id else '',
                    l.kardex_id.location_id.name_get()[0][1] if l.kardex_id.location_id else '',
                    l.transit_location_id.name_get()[0][1] if l.transit_location_id else '',
                    l.counterpart_location_id.name_get()[0][1] if l.counterpart_location_id else '',
                    l.previous_balance_qty,
                    previous_balance_qty,
                    l.in_qty,
                    l.out_qty,
                    l.balance_qty,
                    balance_qty
                ]
                previous_balance_qty = balance_qty

                if self.costing:
                    balance_value = previous_balance_value + l.in_value - l.out_value
                    vals.extend([
                        l.previous_balance_value,
                        previous_balance_value,
                        l.in_value,
                        l.out_value,
                        l.balance_value,
                        balance_value
                    ])
                    previous_balance_value = balance_value
                rows.append(vals)

            sheet.update({
                'rows': rows,
            })
            sheets.append(sheet)

            data.update({
                'sheets': sheets,
            })

        if self.type == 'by_location':
            sheets = []
            for k in kardex:
                sheet = {
                    'name': k.location_id.name,
                }
                rows = []
                header = [
                    _(u'FECHA'),
                    _(u'NOMBRE'),
                    _(u'MOVIMIENTO'),
                    _(u'UBICACIÓN DE TRÁNSITO'),
                    _(u'UBICACIÓN RELACIONADA'),
                    _(u'CANTIDAD ANTERIOR'),
                    _(u'ENTRADAS'),
                    _(u'SALIDAS'),
                    _(u'CANTIDAD FINAL')
                ]

                if self.costing:

                    header.extend([
                        _(u'VALORACIÓN ANTERIOR'),
                        _(u'INGRESO'),
                        _(u'EGRESO'),
                        _(u'VALORACIÓN FINAL')
                    ])

                rows.append(header)

                for l in k.kardex_line_ids:
                    vals = [
                        l.date,
                        l.name,
                        l.picking_id.name_get()[0][1] if l.picking_id else '',
                        l.transit_location_id.name_get()[0][1] if l.transit_location_id else '',
                        l.counterpart_location_id.name_get(
                        )[0][1] if l.counterpart_location_id else '',
                        l.previous_balance_qty,
                        l.in_qty,
                        l.out_qty,
                        l.balance_qty
                    ]

                    if self.costing:
                        vals.extend([
                            l.previous_balance_value,
                            l.in_value,
                            l.out_value,
                            l.balance_value
                        ])
                    rows.append(vals)
                sheet.update({
                    'rows': rows,
                })
                sheets.append(sheet)

            data.update({
                'sheets': sheets,
            })
        return data

    @api.multi
    def button_get_xlsx_report(self):
        data = self.get_report_data()
        wb = openpyxl.Workbook()

        # Seleccionamos la hoja activa para eliminarla.
        aws = wb.active

        sheets = data.get('sheets', [])
        for s in sheets:
            name = s.get('name', 'sheet %s' % sheets.index(s))
            ws = wb.create_sheet(name.replace('/', '-'))
            rows = s.get('rows', [])
            for row in rows:
                ws.append(row)

        # Elimina la hoja principal
        # wb.remove_sheet(aws)

        output = StringIO()
        wb.save(output)
        xlsx_data = output.getvalue()
        self.write({'xlsx_filename': data.get('filename', 'report.xlsx'),
                    'xlsx_file': base64.encodestring(xlsx_data)})

        return {
            'type': 'ir.actions.act_window',
            'res_model': data.get('wizard'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': self._context,
        }
