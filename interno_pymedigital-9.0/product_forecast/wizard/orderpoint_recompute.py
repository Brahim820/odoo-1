# -*- coding: utf-8 -*-

import threading
from openerp import sql_db, models, fields, api, _
from openerp.api import Environment

class OrderPointCompute(models.TransientModel):
    """Compute Minimum and Maximum Stock Rules"""
    _name = 'orderpoint.compute'
    _description = __doc__



    def _calculation_orderpoint(self):
        """
        @param self: The object pointer.
        """
        new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
        uid, context = self.env.uid, self.env.context
        with Environment.manage():
            try:
                self.env = Environment(new_cr, uid, context)
                orderpoint_obj = self.env['stock.orderpoint.line']
                orderpoint_obj.compute_orderpoint()
            finally:
                new_cr.commit()
                new_cr.close()
        return {}

    @api.multi
    def orderpoint_calculation(self):
        """
        @param self: The object pointer.
        """

        threaded_calculation = threading.Thread(target=self._calculation_orderpoint)
        threaded_calculation.start()
        return {'type': 'ir.actions.act_window_close'}
