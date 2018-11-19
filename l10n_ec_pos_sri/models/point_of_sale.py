# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api

class PosConfig(models.Model):
    _inherit = 'pos.config'

    autorizacion_id = fields.Many2one('l10n_ec_sri.autorizacion', string='Autorización', )
