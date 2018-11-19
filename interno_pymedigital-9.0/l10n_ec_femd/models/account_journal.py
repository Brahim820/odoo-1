# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountJournal(models.Model):
    _inherit = ['account.journal']

    collection_md = fields.Selection([
        ('95010101',
         'Ventas de bienes y prestacion de servicios'),
        ('95010102',
         'Regaloas, cuotas, comisiones y otras actividades ordinarias'),
        ('95010103',
         'Contratos mantenidos con propositos de intermediacion'),
        ('95010104',
         'Primas y prestaciones, anualidades y otros beneficios de polizas'),
        ('95010105',
         'Otros cobros por actividades de operacion'), ],
        string='Clasificación del cobro',
        help="Esta clasificación se usará por defecto al seleccionar este diario al realizar un cobro.",
        default='95010101')

    payment_md = fields.Selection([
        ('95010201',
         'Proveedores por el suministro de bienes y servicios'),
        ('95010202',
         'Contratos mantenidos para intermediacion o para negociar'),
        ('95010203',
         'Por cuenta de los empleados'),
        ('95010204',
         'Primas y prestaciones, anualidades y obligaciones de las polizas'),
        ('95010205',
         'Otros pagos por actividades de operacion'), ],
        string='Clasificación del pago',
        help="Esta clasificación se usará por defecto al seleccionar este diario al realizar un pago.",
        default='95010201')
