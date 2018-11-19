#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from openerp import api, fields, models


class WizardCarrierInfo(models.TransientModel):
    _name = 'wizard.carrier.info'

    carrier_id = fields.Many2one('delivery.carrier', string='Transport Company')
    driver_id = fields.Many2one('res.partner', string='Driver')
    licence_plate = fields.Char('Licence Plate')
    route = fields.Char('Route')

    @api.onchange('carrier_id')
    def _onchange_carrier(self):
        driver_ids = []
        if self.carrier_id:
            driver_ids = [x.id for x in self.carrier_id.delivery_carrier_ids]
        return {'domain': {'driver_id': [('id', 'in', driver_ids)]}}

    @api.one
    def generar_guia_remision(self):
        picking_id = self.env['stock.picking'].browse(self._context.get('active_ids', False))
        vals = {
            'carrier_id': self.carrier_id.id,
            'driver_id': self.driver_id.id if self.driver_id else self.carrier_id.partner_id.id,
            'carrier_tracking_ref': self.licence_plate,
            'route': self.route,
            'fechainitransporte': datetime.today(),
            'fechafintransporte': datetime.today() + timedelta(days=2),
        }
        if picking_id:
            picking_id.write(vals)
            picking_id.button_send_guia_remision_electronica()
        return True
