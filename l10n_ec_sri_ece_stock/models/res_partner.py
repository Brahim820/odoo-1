# -*- coding: utf-8 -*-
from openerp import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    enviar_guias_de_remision_electronicas = fields.Boolean(
        string='Enviar guías de remisión electrónicas',
        default=True,
    )

