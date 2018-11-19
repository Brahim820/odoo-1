# -*- coding: utf-8 -*-

import threading
from openerp import sql_db, models, fields, api, _
from openerp.api import Environment


class SummaryCompute(models.TransientModel):
    """Compute product summary"""
    _name = 'product.summary.compute'
    _description = __doc__

    def _default_month(self):
        mes = fields.datetime.now().strftime("%m")
        if mes == '01':
            default = '12'
        else:
            default = str(int(mes) - 1).zfill(2)
        return default

    def _default_year(self):
        return fields.datetime.now().strftime("%Y")

    def _list_years(self):
        list_years = []
        self._cr.execute("select date_part('year',date) from account_move limit 1;")
        current_year = int(fields.datetime.now().strftime("%Y"))
        first_year = self._cr.fetchone()
        first_year = int(first_year[0] if first_year else current_year)
        if first_year and first_year != current_year:
            for year in range(first_year, current_year + 1):
                list_years.append((str(year), str(year)))
        else:
            list_years = [(str(current_year), str(current_year))]
        return list_years

    month = fields.Selection(
        [
            ('01', _('January')),
            ('02', _('February')),
            ('03', _('March')),
            ('04', _('April')),
            ('05', _('May')),
            ('06', _('June')),
            ('07', _('July')),
            ('08', _('August')),
            ('09', _('September')),
            ('10', _('October')),
            ('11', _('November')),
            ('12', _('December'))
        ],
        string='Month',
        default=_default_month,
        required=True)
    year = fields.Selection(
        _list_years, string="Year", required=True,
        default=_default_year)
    product_ids = fields.Many2many(
        'product.product', 'product_summary_wiz_rel',
        'product_id', 'summary_id', string='Products',
        required=True)

    def _calculation_summary(self):
        """
        @param self: The object pointer.
        """
        new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
        uid, context = self.env.uid, self.env.context
        with Environment.manage():
            try:
                self.env = Environment(new_cr, uid, context)
                summary_obj = self.env['product.summary']
                summary_obj.get_summary(
                    int(self.month), int(self.year),
                    self.product_ids)
            finally:
                new_cr.commit()
                new_cr.close()
        return {}

    @api.multi
    def summary_calculation(self):
        """
        @param self: The object pointer.
        """

        threaded_calculation = threading.Thread(target=self._calculation_summary)
        threaded_calculation.start()
        return {'type': 'ir.actions.act_window_close'}
