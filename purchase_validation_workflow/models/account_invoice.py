# -*- coding: utf-8 -*-
from openerp import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    block_payment = fields.Char('Payment blocked reasons', )
    disallow_payment = fields.Boolean('Payment aproved', default=True, )

    @api.multi
    def button_allow_payment(self):
        self.write({
            'disallow_payment': False,
            'block_payment': ''
        })

    @api.multi
    def validate_payment(self):

        block_payment = ''
        for i in self.invoice_line_ids:
            nro = 1

            if not i.purchase_line_id:
                continue

            if i.price_unit > i.purchase_line_id.price_unit:
                block_payment += str(nro) + '.- El precio del producto ' + str(i.product_id.name) + \
                    ' es superior al precio acordado con el proveedor. '
                nro += 1

        if block_payment == '':
            self.disallow_payment = False
        else:
            self.block_payment = block_payment
