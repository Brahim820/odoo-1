# -*- coding: utf-8 -*-
from openerp import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    autorizacion_guias_remision_id = fields.Many2one(
        'l10n_ec_sri.autorizacion',
        string='Autorizacion en guías de remisión', )

