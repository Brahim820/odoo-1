# -*- coding: utf-8 -*-

from openerp import models, fields, api


class PosConfig(models.Model):
    _inherit = 'pos.config'

    puntoemision = fields.Integer('Punto de emisión', )
    establecimiento = fields.Integer('Establecimiento', )
    secuencial = fields.Integer('Secuencial')
    autorizacion = fields.Integer('Autorización')

    # BORRAR
    # autorizacion_id = fields.Many2one('l10n_ec_sri.autorizacion', string='Autorizacion', )

    def save_config_from_pos(self, cr, uid, config_id, to_write, context=None):
        self.browse(cr, uid, config_id, context=context).sudo().write(to_write)

class PosOrder(models.Model):
    _inherit = 'pos.order'

    puntoemision = fields.Integer('Punto de emisión', )
    establecimiento = fields.Integer('Establecimiento', )
    secuencial = fields.Integer('Secuencial')
    autorizacion = fields.Integer('Autorización')

    @api.multi
    def action_invoice(self):
        res = super(PosOrder, self).action_invoice()
        res_id = res['res_id']
        res_model = res['res_model']
        inv = self.env[res_model].browse(res_id)
        inv.compute_sri_invoice_amounts()
        return res

    def _process_order(self, cr, uid, order, context=None):
        order_id = super(PosOrder, self)._process_order(cr, uid, order, context=context)
        if order_id:
            to_write = {
                'secuencial': order.get('secuencial', None),
                'autorizacion': order.get('autorizacion', None),
                'puntoemision': order.get('puntoemision', None),
                'establecimiento': order.get('establecimiento', None),
            }
            self.write(cr, uid, order_id, to_write, context=context)

            config = self.browse(cr, uid, order_id, context=context)
            config = config.config_id if config else None
            if config:
                if config.secuencial > to_write['secuencial']:
                    to_write['secuencial'] = config.secuencial
                config.sudo().write(to_write)
        return order_id

