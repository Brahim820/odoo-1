#!/usr/bin/env python
# -*- coding: utf-8 -*-
from openerp import _, api, fields, models


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    delivery_carrier_ids = fields.Many2many('res.partner', 'l10n_ec_delivery_carrier_rel',
                                            'partner_id', 'delivery_id', string="Carriers", copy=False)
