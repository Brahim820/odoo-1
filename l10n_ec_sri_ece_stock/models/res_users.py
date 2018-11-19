# -*- coding: utf-8 -*-

from openerp import models, fields
class ResUsers(models.Model):
    _inherit = 'res.users'

    autorizacion_guias_remision_id = fields.Many2one(
        'l10n_ec_sri.autorizacion',
        string='Autorizacion en guías de remisión', )

