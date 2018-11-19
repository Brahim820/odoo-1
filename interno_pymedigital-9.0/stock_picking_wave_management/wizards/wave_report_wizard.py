# -*- coding: utf-8 -*-
import base64
from cStringIO import StringIO

import logging
_logger = logging.getLogger(__name__)

from openerp import models, fields, api, _

try:
    import openpyxl
except ImportError:
    _logger.error("The module openpyxl can't be loaded, try: pip install openpyxl")


class WaveReportWizard(models.TransientModel):
    _name = 'wave.report.wizard'

    wave_id = fields.Many2one('stock.picking.wave', 'Picking Wave', )
    file = fields.Binary('Production', attachment=True, readonly=True, )
    filename = fields.Char(string="Production filename", )

    # Header
    include_partner = fields.Boolean('Include partner', default=True, )
    include_warehouse = fields.Boolean('Include warehouse', default=False, )

    @api.multi
    def get_production_report(self):
        productions = self.wave_id.procurement_production_ids
        routes = productions.mapped('routing_id')
        pickings = self.wave_id.picking_ids

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = u'ORDENES DE PRODUCCIÓN'

        for route in routes:
            ws.append([route.name])

            if self.include_partner:
                partner_header = ['','']
                for picking in pickings:
                    partner_header.append(picking.partner_id.name)
                ws.append(partner_header)

            if self.include_warehouse:
                warehouse_header = ['','']
                for picking in pickings:
                    warehouse_header.append(picking.location_dest_id.location_id.name)
                ws.append(warehouse_header)

            header = [
                _('PRODUCT'),
                _('TOTAL'),
            ]
            for picking in pickings:
                header.append(picking.name)
            ws.append(header)

            prod_obj = productions.filtered(lambda p: p.routing_id == route)

            for p in prod_obj:
                production_list = [
                    p.product_id.name,
                ]

                total = 0
                picking_list = []
                for sp in pickings:
                    move = sp.move_lines_related.filtered(lambda x: x.product_id == p.product_id)
                    m = sum(move.mapped('product_uom_qty'))
                    picking_list.append(m or 0)
                    total += m

                production_list.append(total)

                production_list += picking_list

                ws.append(production_list)

            # Genera un espacio vacío entre rutas.
            ws.append([
                '',
            ])

        output = StringIO()
        wb.save(output)

        xlsx_data = output.getvalue()
        self.write({'filename': 'produccion.xlsx',
                    'file': base64.encodestring(xlsx_data)})

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'wave.report.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': self._context,
        }
