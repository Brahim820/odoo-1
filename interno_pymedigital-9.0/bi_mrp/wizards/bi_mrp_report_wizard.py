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

STATE = {
    'done': _('Done'),
    'confirmed': _('Awaiting raw materials'),
    'ready': _('Ready to produce'),
    'in_production': _('Production started'),
    'canceled': _('Cancelled'),
    'draft': _('Draft'),
    'partial': _('Partially done'),
}


class BiMrpReportWizard(models.TransientModel):
    _name = 'bi.mrp.report.wizard'

    xlsx_file = fields.Binary('Production', attachment=False, readonly=True, )
    xlsx_filename = fields.Char(string="Production filename", )
    type = fields.Selection([
        ('detailed', 'Detailed'),
        ('consumption', 'Consumption'),
    ], default="detailed",
        string='Type',
    )

    valuation = fields.Boolean(string='Valuation', )

    # Header
    done = fields.Boolean(string='Done', default=True,)
    confirmed = fields.Boolean(string='Confirmed', )
    ready = fields.Boolean(string='Ready', )
    in_production = fields.Boolean(string='In production', )
    cancel = fields.Boolean(string='Cancelled', )
    draft = fields.Boolean(string='Draft', )

    production_ids = fields.Many2many(
        'mrp.production',
        'production_wizard_rel',
        'wizard_ids',
        'production_ids',
        string='Productions', )
    product_ids = fields.Many2many(
        'product.product',
        'product_wizard_rel',
        'wizard_ids',
        'product_ids',
        string='Products variants', )
    template_ids = fields.Many2many(
        'product.template',
        'template_wizard_rel',
        'wizard_ids',
        'template_ids',
        string='Product templates', )
    category_ids = fields.Many2many(
        'product.category',
        'category_wizard_rel',
        'wizard_ids',
        'category_ids',
        string='Categories', )
    date_from = fields.Datetime(string='Date from', )
    date_to = fields.Datetime(string='Date to', )

    @api.multi
    def get_production_report_detail(self, p, valuation):
        lines = []

        # Por defecto el campo 'valuation' es false. Tomando esto como base, la variable 'dict_properties_positions'
        # presupondrá una posición para cada campo, pero en caso de que el campo 'valuation' sea modificado, se va
        # a usar esta variable (sumar_posicion) para sumar la cantidad de campos que se ubicaron antes
        sumar_posicion = 0
        sumar_posicion_para_scrap = 0
        dict_properties_positions = {}

        # Warehouse
        wh = p.location_src_id.location_id.name

        # product.product
        required = p.product_id

        # mrp.production.product.line
        planned = p.product_lines

        # stock.move
        done = p.move_created_ids2
        to_do = p.move_created_ids
        consumed = p.move_lines2
        to_consume = p.move_lines

        # Raw materials.
        raw_moves = consumed + to_consume
        raw_products = raw_moves.mapped('product_id')

        # Finished move lines.
        finished_moves = done + to_do

        # Byproducts
        by_products = finished_moves.filtered(
            lambda l: l.product_id != required).mapped('product_id')

        # Production uoms
        p_uom = p.product_uom
        # Unidad del producto principal required
        r_uom = required.uom_id

        bom_uom = p.bom_id.product_uom
        # unidad de medida de referencia.
        ref_uom = r_uom.search(
            [('category_id', '=', r_uom.category_id.id),
             ('uom_type', '=', 'reference')
             ]
        )
        # No procesar el reporte si las unidades de medida son incompatibles.
        if p_uom.category_id != r_uom.category_id or p_uom.category_id != bom_uom.category_id:
            # ws.append([p.name, required.name, 'UOM INCOMPATIBLE'])
            return [[p.name, required.name, 'UOM INCOMPATIBLE']]

        produced_moves = finished_moves.filtered(
            lambda l: l.product_id == required
                      and l.state == 'done')
        real_moves = produced_moves.filtered(
            lambda l: not l.scrapped)
        real_qty = sum(real_moves.mapped('product_uom_qty'))
        real_valuation = sum(real_moves.mapped('quant_ids').mapped('inventory_value'))
        discrepancy_qty = real_qty - p.product_qty
        scrapped_moves = produced_moves.filtered(
            lambda l: l.scrapped)
        scrapped_qty = sum(scrapped_moves.mapped('product_uom_qty'))
        scrapped_valuation = sum(scrapped_moves.mapped(
            'quant_ids').mapped('inventory_value'))

        vals = [
            wh,
            p.name,
            p.bom_id.code or '',
            p.state,
            p.date_planned or None,
            p.create_date or None,
            p.date_start or None,
            p.date_finished or None,
            required.default_code or '',
            required.name or '',
            p.product_uom.name,
            p.product_qty,
            real_qty
        ]

        if valuation:
            vals.extend([real_valuation])
            sumar_posicion += 1

        vals.extend([
            discrepancy_qty,
            scrapped_qty,
        ])

        if valuation:
            vals.extend([scrapped_valuation])
            sumar_posicion += 1

        vals.extend([
            r_uom.name,
            p.product_uom._compute_qty(p_uom.id, p.product_qty, r_uom.id),
            ref_uom.name,
            p.product_uom._compute_qty(p_uom.id, p.product_qty, ref_uom.id),
        ])


        dict_properties_positions = {
            'mp_name': 19 + sumar_posicion,
            'mp_code': 20 + sumar_posicion,
            'mp_uom_name': 21 + sumar_posicion,
            'mp_planificada': 22 + sumar_posicion,
            'mp_consumida': 23 + sumar_posicion,
            'mp_desechada': 24 + sumar_posicion,
            'mp_diferencia': 25 + sumar_posicion
        }

        for raw in raw_products:
            # # Si usamos line = vals se actualiza vals en cada línea.
            line = []
            line.extend(vals)

            # Reiniciamos los valores
            raw_real_qty = raw_scrapped_qty = 0
            raw_discrepancy_qty = raw_standard_qty = 0
            raw_standard_qty = sum(planned.filtered(
                lambda l: l.product_id == raw).mapped('product_qty'))
            raw_move_lines = raw_moves.filtered(
                lambda l: l.product_id == raw and l.state == 'done')
            raw_real_moves = raw_move_lines.filtered(
                lambda l: not l.scrapped)
            raw_real_qty = sum(raw_real_moves.mapped('product_uom_qty'))
            raw_real_valuation = sum(raw_real_moves.mapped(
                'quant_ids').mapped('inventory_value'))
            raw_scrapped_moves = raw_move_lines.filtered(
                lambda l: l.scrapped)

            raw_scrapped_qty = abs(sum(raw_scrapped_moves.mapped('product_uom_qty')))
            raw_scrapped_valuation = sum(raw_scrapped_moves.mapped(
                'quant_ids').mapped('inventory_value'))

            raw_discrepancy_qty = raw_real_qty - raw_standard_qty
            # Si se incrementa un campo en esta lista es necesario incrementar un espacio en blanco
            # en la lista de by_products.
            line.extend([
                raw.name or '',# position 19 in the line
                raw.default_code or '',
                raw.uom_id.name,
                raw_standard_qty,
                raw_real_qty
            ])
            if valuation:
                line.extend([raw_real_valuation])
                sumar_posicion_para_scrap = sumar_posicion + 1

            dict_properties_positions['mp_desechada'] = 24 + sumar_posicion_para_scrap

            line.extend([
                raw_scrapped_qty
            ])

            if valuation:
                line.extend([raw_scrapped_valuation])
                sumar_posicion_para_scrap = sumar_posicion + 2

            dict_properties_positions['mp_diferencia'] = 25 + sumar_posicion_para_scrap
            line.extend([
                raw_discrepancy_qty
            ])
            if valuation:
                line.extend([raw_discrepancy_qty * raw.standard_price])
            lines.append(line)

        if valuation:
            sumar_posicion += 3

        dict_properties_positions['subproducto_nombre'] = 26 + sumar_posicion
        dict_properties_positions['subproducto_codigo'] = 27 + sumar_posicion
        dict_properties_positions['subproducto_uom'] = 28 + sumar_posicion
        dict_properties_positions['subproducto_plan'] = 29 + sumar_posicion
        dict_properties_positions['subproducto_real'] = 30 + sumar_posicion
        dict_properties_positions['subproducto_diff'] = 31 + sumar_posicion

        for by in by_products:
            # Si usamos line = vals se actualiza vals en cada línea.
            line = []
            line.extend(vals)

            by_line = p.bom_id.sub_products.filtered(lambda l: l.product_id == by)
            if len(by_line) > 1:
                raise UserError(
                    _('La lista de Materiales para el Producto {}, tiene inconsistencias con el sub producto {}'.format(
                        p.bom_id.name_get()[0][1], by.name_get()[0][1])))

            by_standard_qty = by_line.product_qty
            if by_line.subproduct_type == 'variable':
                uom_qty = p.product_uom._compute_qty(
                    p.product_uom.id, p.product_qty, p.bom_id.product_uom.id)
                uom_factor = uom_qty / (p.bom_id.product_qty or 1.0)

                by_standard_qty *= uom_factor

            by_real_moves = finished_moves.filtered(
                lambda l: l.product_id == by
                          and not l.scrapped
                          and l.state == 'done')

            by_real_qty = sum(by_real_moves.mapped('product_uom_qty'))
            by_real_valuation = sum(by_real_moves.mapped(
                'quant_ids').mapped('inventory_value'))
            by_discrepancy_qty = by_real_qty - by_standard_qty

            line.extend([
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                by.name or '',# position 26 in the line
                by.default_code or '',
                by.uom_id.name,
                by_standard_qty,
                by_real_qty,
            ])

            if valuation:
                line.extend([by_real_valuation])

            line.extend([
                by_discrepancy_qty,
            ])
            lines.append(line)

        return lines, dict_properties_positions

    @api.multi
    def get_production_report(self):
        production_filter = []
        if self.production_ids:
            productions = self.production_ids

        else:
            if self.done \
                    or self.confirmed \
                    or self.ready \
                    or self.in_production \
                    or self.canceled \
                    or self.draft:

                states = []

                if self.done:
                    states.append('done')
                if self.confirmed:
                    states.append('confirmed')
                if self.ready:
                    states.append('ready')
                if self.in_production:
                    states.append('in_production')
                if self.cancel:
                    states.append('cancel')
                if self.draft:
                    states.append('draft')

                production_filter.append(('state', 'in', states))

            if self.date_from:
                production_filter.append(('date_planned', '>=', self.date_from))
            if self.date_to:
                production_filter.append(('date_planned', '<=', self.date_to))

            mo = self.env['mrp.production'].search(production_filter)

            productions = self.env['mrp.production']
            if self.product_ids:
                productions = mo.filtered(lambda x: x.product_id in self.product_ids)
            if self.template_ids:
                productions = productions | mo.filtered(
                    lambda x: x.product_tmpl_id in self.template_ids)
            if self.category_ids:
                productions = productions | mo.filtered(
                    lambda x: x.product_tmpl_id.categ_id in self.category_ids)

            productions = productions or mo

        uom_obj = self.env['product.uom']

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = u'ORDENES DE PRODUCCIÓN'

        if self.type == 'detailed':
            header = [
                _(u'BODEGA MP'),
                _(u'ORDEN DE PRODUCCIÓN'),
                _(u'LISTA DE MATERIALES'),
                _(u'ESTADO'),
                _(u'PLANIFICADA'),
                _(u'CREACIÓN '),
                _(u'INICIO'),
                _(u'CIERRE '),
                _(u'CÓDIGO '),
                _(u'DESCRIPCIÓN '),
                _(u'UOM MO'),
                _(u'CANT. MO'),
                _(u'CANT. REAL MO')
            ]

            if self.valuation:
                header.extend([
                    _('VALOR REAL MO')
                ])

            header.extend([
                _(u'DIFERENCIA MO'),
                _(u'CANT. DESECHADA MO'),
            ])

            if self.valuation:
                header.extend([
                    _('VALOR DESECHO MO')
                ])

            header.extend([
                _(u'UOM PRODUCTO'),
                _(u'CANT. UOM PROD.'),
                _(u'UOM REF.'),
                _(u'CANT. UOM REF.'),
                _(u'MATERIA PRIMA '),
                _(u'CÓDIGO MP'),
                _(u'UOM MP'),
                _(u'MP CONSUMO PLANEADO'),
                _(u'MP CONSUMO REAL')
            ])
            if self.valuation:
                header.extend([
                    _(u'VALORACIÓN CONSUMO')
                ])

            header.extend([
                _(u'MP DESECHADO'),
            ])
            if self.valuation:
                header.extend([
                    _(u'MP VALOR DESECHO')
                ])

            header.extend([
                _(u'MP DIFERENCIA'),
            ])
            if self.valuation:
                header.extend([
                    _(u'MP VALOR DIFERENCIA')
                ])

            header.extend([
                _(u'SUBPRODUCTO'),
                _(u'CÓDIGO SP'),
                _(u'UOM SP'),
                _(u'SP PLANEADO'),
                _(u'SP REAL'),
            ])

            if self.valuation:
                header.extend([
                    _('SP VALOR')
                ])

            header.extend([
                _(u'SP DIFERENCIA')
            ])
            ws.append(header)

            for p in productions:
                new_lines = self.get_production_report_detail(p, self.valuation)

                for line in new_lines:
                    ws.append(line)

        elif self.type == 'consumption':
            header = [
                _(u'CODIGO'),
                _(u'MATERIA PRIMA'),
                _(u'UOM'),
                _(u'CANTIDAD CONSUMIDA'),
                _(u'CONSUMO MENSUAL PROMEDIO'),
                _(u'EXISTENCIAS NO RESERVADAS'),
                _(u'EXISTENCIAS'),
                _(u'POR RECIBIR'),
                _(u'POR ENTREGAR'),
                _(u'DISPONIBILIDAD ESPERADA'),
            ]
            ws.append(header)
            moves = productions.mapped('move_lines2')
            moves = moves.filtered(lambda x: x.state == 'done')
            raw = moves.mapped('product_id')

            months = 1.00
            if self.date_from and self.date_to:
                date_from = fields.Datetime.from_string(self.date_from)
                date_to = fields.Datetime.from_string(self.date_to)

                months = float(abs((date_from - date_to).days)) / 30

            for r in raw:

                consumed = sum(moves.filtered(lambda x: x.product_id == r).mapped('product_qty'))
                vals = [
                    r.default_code or '',
                    r.name or '',
                    r.uom_id.name or '',
                    consumed,
                    consumed / months,
                    r.qty_available_not_res,
                    r.qty_available,
                    r.incoming_qty,
                    r.outgoing_qty,
                    r.virtual_available,
                ]
                ws.append(vals)

        output = StringIO()
        wb.save(output)

        xlsx_data = output.getvalue()
        self.write({'xlsx_filename': 'produccion.xlsx',
                    'xlsx_file': base64.encodestring(xlsx_data)})

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'bi.mrp.report.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': self._context,
        }
