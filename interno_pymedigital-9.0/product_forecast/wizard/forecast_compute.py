# -*- coding: utf-8 -*-

import threading
from openerp import sql_db, models, fields, api, _
from openerp.api import Environment


class ProductForecast(models.TransientModel):
    """Compute Stock Forecast"""
    _name = 'forecast.compute'
    _description = __doc__

    def _list_years(self):
        list_years = []
        current_year = int(fields.datetime.now().strftime("%Y"))
        for year in range(current_year, current_year + 3):
            list_years.append((str(year), str(year)))
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
    )

    year = fields.Selection(
        _list_years, string="Year")
    forecast_type = fields.Selection(
        [('mobile_avg', 'Mobile Average'), ('time_series', 'Time series')],
        'Forecast type', required=True)
    product_ids = fields.Many2many(
        'product.product', 'product_forecast_wiz_rel',
        'product_id', 'forecast_id', string='Products',
        domain=[('sale_ok', '=', True)],
        required=True)
    historic_periods = fields.Selection(
        [('3', '3'), ('6', '6')],
        'Historic periods', default='3')
    forecast_periods = fields.Selection(
        [('3', '3'), ('6', '6'), ('9', '9'), ('12', '12')],
        'Forecast periods', default='3')
    grow_percent = fields.Float('Grow percent')
    run_background = fields.Boolean('Run in background', default=True)

    def _calculation_forecast(self):
        """
        @param self: The object pointer.
        """
        new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
        uid, context = self.env.uid, self.env.context
        with Environment.manage():
            try:
                self.env = Environment(new_cr, uid, context)
                summary_obj = self.env['product.summary']
                if self.forecast_type == 'mobile_avg':
                    summary_obj.get_avg_mobile_forecast(
                        int(self.month), int(self.year),
                        int(self.historic_periods), int(self.forecast_periods), self.product_ids, self.grow_percent)
                else:
                    summary_obj.get_time_series_forecast(
                        int(self.month), int(self.year),
                        int(self.forecast_periods), self.product_ids, self.grow_percent)
            finally:
                new_cr.commit()
                new_cr.close()
        return {}

    @api.multi
    def forecast_calculation(self):
        """
        @param self: The object pointer.
        """
        if self.run_background:
            threaded_calculation = threading.Thread(target=self._calculation_forecast)
            threaded_calculation.start()
        else:
            summary_obj = self.env['product.summary']
            if self.forecast_type == 'mobile_avg':
                summary_obj.get_avg_mobile_forecast(
                    int(self.month), int(self.year),
                    int(self.historic_periods), int(self.forecast_periods), self.product_ids, self.grow_percent)
            else:
                summary_obj.get_time_series_forecast(
                    int(self.month), int(self.year),
                    int(self.forecast_periods), self.product_ids, self.grow_percent)
        return {'type': 'ir.actions.act_window_close'}
