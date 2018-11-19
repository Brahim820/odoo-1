# -*- coding: utf-8 -*-
from openerp import models, fields


class Genero(models.Model):
    _name = 'base.genero'

    name = fields.Char(string="Genero y Numero", readonly=True, )
    el = fields.Char(string="el/la/los", readonly=True, )
    deel = fields.Char(string="del/de la/de los", readonly=True, )
    o = fields.Char(string="o/a/os", readonly=True, )
    e = fields.Char(string="e/es", readonly=True, )
    es = fields.Char(string="/es", readonly=True, )
    son = fields.Char(string="es/son", readonly=True, )
    a = fields.Char(string=" /a/es", readonly=True, )
    n = fields.Char(string="n", readonly=True, )
    s = fields.Char(string="s", readonly=True, )
    lo = fields.Char(string="lo/la/os", readonly=True, )
    al = fields.Char(string="al/a la/a los", readonly=True, )
    compania = fields.Boolean(
        string="Es Compania", readonly=True,
        help="Seleccione si la redaccion aplica a una compania", )
    code = fields.Char(string='Código', required=True, readonly=True, )
