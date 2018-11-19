# -*- coding: utf-8 -*-
from openerp import models, fields, api


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def propagate_wave(self, wave, order):
        if order.requisition_id:
            order.requisition_id.write({'wave_id': wave, })
        return super(ProcurementOrder, self).propagate_wave(wave, order)


class StockPickingWave(models.Model):
    _inherit = 'stock.picking.wave'

    # Purchase requisitions generated by a procurement on the wave.
    procurement_requisition_ids = fields.One2many('purchase.requisition', 'wave_id', string='Pruchase requsitions', )
