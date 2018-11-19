# -*- coding: utf-8 -*-
from openerp import models, fields

class Docs(models.Model):
    _name = 'extra_internal_docs.docs'

    name = fields.Char('Documento')

class VoidDocs(models.Model):
    _name = 'extra_internal_docs.voiddocs'

    fecha = fields.Date('Fecha de anulación', )
    journal_id = fields.Many2one(
        'account.journal', string='Diario', )
    secuencialinicio = fields.Integer(
        'Secuencial inicial',
        required=True, )
    secuencialfin = fields.Integer(
        'Secuencial final',
        required=True, )
    docs_id = fields.Many2one(
        'extra_internal_docs.docs', string='Documento', )
