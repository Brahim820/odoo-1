# -*- coding: utf-8 -*-

# from openerp import fields, models, api

from openerp.osv import fields, osv
from openerp import api

import openerp.addons.decimal_precision as dp

class StockMove(osv.osv):
    _inherit = 'stock.move'

    _columns = {
        'planned_qty': fields.float('Product Quantity', digits_compute=dp.get_precision('Product Unit of Measure'),
                                    compute='_compute_planed'),
        'diff_qty': fields.float('Product Quantity', digits_compute=dp.get_precision('Product Unit of Measure'),
                                 compute='_compute_diff'),
    }

    @api.depends('production_id', 'product_uom_qty')
    def _compute_planed(self):
        for rec in self:
            l = self.env['mrp.production.product.line'].search([['production_id', '=', rec.production_id.id], ['product_id', '=', rec.product_id.id]])
            rec.diff_qty = rec.product_uom_qty # HAY QUE ARREGLAR LA FORMULA PARA OBTENER EL VALOR

    @api.depends('planned_qty', 'product_uom_qty')
    def _compute_diff(self):
        for rec in self:
            rec.diff_qty = rec.planned_qty - rec.product_uom_qty



    def action_production_end(self, cr, uid, ids, context=None):
        """ Changes production state to Finish and writes finished date.
        @return: True
        """
        self._compute_costs_from_production(cr, uid, ids, context)
        write_res = self.write(cr, uid, ids, {'state': 'done', 'date_finished': time.strftime('%Y-%m-%d %H:%M:%S')})
        # Check related procurements
        proc_obj = self.pool.get("procurement.order")
        procs = proc_obj.search(cr, uid, [('production_id', 'in', ids)], context=context)
        proc_obj.check(cr, uid, procs, context=context)
        return write_res