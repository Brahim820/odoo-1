# -*- coding: utf-8 -*-

from openerp import api, fields, models, _


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model
    def update_old_names(self):

        old_line_ids = self.search([('name', '=', '/')])
        for line in old_line_ids:
            inv_ids = self.env['account.invoice'].search([('move_id', '=', line.move_id.id)])
            if inv_ids:
                new_line_name = inv_ids[0].get_sri_secuencial_completo_factura()
                if inv_ids[0].reference:
                    new_line_name = '%s %s' % (inv_ids[0].reference, new_line_name)

                line.write({'name': new_line_name})
