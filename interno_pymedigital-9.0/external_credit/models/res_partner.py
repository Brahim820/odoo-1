# -*- coding: utf-8 -*-
####################################################
# Parte del Proyecto LibreGOB: http://libregob.org #
# Licencia AGPL-v3                                 #
####################################################

from openerp import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    code = fields.Char(string='Code', required=True)
    committee_groups = fields.Selection([
            ('ce','ComiteEmpresa'),
            ('st','SindicatoTrabajadores'),
            ('se','SindicatoEmpleados'),
            ('np','Nopertenece'),
        ], default="np",
        string='Committee Groups',
        required=True,
        )

    credit_ids = fields.One2many(
        'credit.credit',
        'partner_id',
        string='Credits',
         )





