from calendar import monthrange
from datetime import datetime

from openerp import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.depends('summary_ids', 'mad_periods')
    def _compute_mad(self):
        """
        Compute Mean Squared error of a product
        :return:
        """
        for rec in self:
            mad = 0.0
            summaries = rec.summary_ids.search(
                [('date', '<=', datetime.today()), ('product_id', '=', rec.id)],
                limit=rec.mad_periods, order='date desc')
            for item in summaries:
                mad += item.forecast_error
            try:
                self.MAD = mad / len(summaries)
            except ZeroDivisionError:
                pass

    summary_ids = fields.One2many(
        'product.summary',
        'product_tmpl_id',
        string='Product Summary')
    mad_periods = fields.Integer('MAD Periods', default=6)
    MAD = fields.Float('Mean absolute deviation', compute="_compute_mad")


class ProductSummary(models.Model):
    _name = 'product.summary'
    _description = 'Inventory Summary in purchase, sales and production'
    _order = 'year,month,product_id asc'

    @api.depends('sales', 'consume')
    def _compute_total(self):
        """
        Compute unit error
        """
        for rec in self:
            rec.total = rec.sales + rec.consume

    @api.depends('total', 'forecast')
    def _forecast_error(self):
        """
        Compute unit error
        """
        for rec in self:
            rec.forecast_error = abs(rec.total - rec.forecast)

    @api.depends('month', 'year')
    def _compute_date(self):
        """
        Define a date to use in queries
        """
        for rec in self:
            if rec.year and rec.month:
                rec.date = '{}-{}-{}'.format(rec.year, rec.month, 1)

    product_id = fields.Many2one('product.product', 'Product')
    product_tmpl_id = fields.Many2one(
        'product.template', 'Product', related='product_id.product_tmpl_id', store=True)
    uom_id = fields.Many2one('product.uom', 'UoM', related='product_id.uom_id')
    month = fields.Integer('Month', required=True)
    year = fields.Integer('Year', required=True)
    date = fields.Date('Date', compute='_compute_date', store="1")
    purchases = fields.Float('Purchases')
    sales = fields.Float('Sales')
    productions = fields.Float('Productions')
    consume = fields.Float('Consume')
    total = fields.Float('Total', compute='_compute_total')
    forecast = fields.Float('Forecast')
    forecast_error = fields.Float('Forecast error', compute='_forecast_error')
    forecast_summary_ids = fields.One2many('product.forecast.summary', 'summary_line_id',
                                           'Required raw qty for Product MRP')

    @api.model
    def get_summary(self, month, year, product_ids=None):
        cdata = {}
        uom_obj = self.env['product.uom']
        where_clause = ''
        if product_ids:
            if len(product_ids) == 1:
                prods = product_ids.id
                op = '='
                where_clause = "AND product_id %s '%s'" % (op, prods)
            else:
                prods = list()
                for product in product_ids:
                    prods.append(product.id)
                prods = tuple(prods)
                op = 'in'
                where_clause = "AND product_id %s %s" % (op, prods)

        query = "SELECT product_id, doc_uom_id, uom_id, doc_type, qty \
        FROM view_product_summary WHERE year = {} AND month = {} \
        {}".format(year, month, where_clause)

        self._cr.execute(query)

        for line in self._cr.fetchall():
            if not cdata or not cdata.get(line[0], False):
                data = {
                    line[0]: {
                        'product_id': line[0],
                        'month': month,
                        'year': year,
                        'purchases': 0,
                        'productions': 0,
                        'sales': 0,
                        'consume': 0
                    }
                }
                cdata.update(data)
            consumption = 0
            if line[1] != line[2]:
                consumption += uom_obj._compute_qty_obj(
                    line[1], float(line[4]), line[2])
            else:
                consumption += line[4]
            if line[3] == 'in_invoice':
                cdata[line[0]]['purchases'] += consumption
            elif line[3] == 'out_invoice':
                cdata[line[0]]['sales'] += consumption
            elif line[3] == 'mrp_production':
                cdata[line[0]]['productions'] += consumption
            elif line[3] == 'mrp_consumption':
                cdata[line[0]]['consume'] += consumption

        for x, y in cdata.items():
            data_id = self.search([('product_id', '=', y['product_id']),
                                   ('month', '=', y['month']),
                                   ('year', '=', y['year'])])
            if data_id:
                data_id.write(y)
            else:
                self.create(y)

    @api.model
    def _compute(self):
        today = datetime.today()
        current_month = today.month
        current_year = today.year
        month_range = monthrange(current_year, current_month)
        fist_day_of_month = '{}/{}/{}'.format(
            month_range[0], current_month, current_year)
        # If this day is the first day of month, then compute
        if today == datetime.strptime(fist_day_of_month, '%d/%m/%Y'):
            # The past month
            month = today.month if current_month == 1 else 12
            year = today.year if current_month == 1 else today.year - 1
            self.get_summary(month, year)

    @api.model
    def get_avg_mobile_forecast(self, month, year, historic_periods, forecast_periods, product_ids=None,
                                grow_percent=0.0):
        """
        Compute mobile average
        :param month:
        :param year:
        :param historic_periods:
        :param forecast_periods:
        :param product_ids:
        :param grow_percent:
        :return:
        """

        periods = []
        month_range = range(1, 13)
        today = datetime.today()
        current_month = month if month else today.month
        current_year = year if year else today.year

        # Build where date clause
        where_clause = ' ( '
        for i in range(1, historic_periods + 1):
            period = month_range[current_month - 1 - i]
            year = current_year
            if period > current_month:
                year = current_year - 1
            periods.append([period, year])
            where_clause += " (month = %d AND year = %d) " % (period, year)
            if i != historic_periods:
                where_clause += " OR "
        where_clause += " ) "

        # Product by product compute forecast
        for product in product_ids:
            op = '='
            product_clause = "AND product_id %s '%s'" % (op, product.id)

            # Get historic data
            query = "SELECT product_id, year, month, sales, consume, forecast AS total \
                     FROM product_summary \
                     where {} {} \
                     ORDER by product_id, year, month;".format(where_clause, product_clause)
            self._cr.execute(query)

            records = self._cr.fetchall()
            if not records:
                continue

            # Compute months forecast
            month = current_month
            year = current_year
            for i in range(forecast_periods):
                # Current month forecast
                forecast = 0.0
                for line in records:
                    forecast += (line[3] + line[4]) or line[5]
                forecast /= historic_periods
                # Apply grow percent
                forecast = forecast + \
                    (forecast * (grow_percent / 100)) if grow_percent else forecast

                # Remove the first record and create a new one
                records.pop(0)
                records.append((product.id, year, month, 0.0, 0.0, forecast))
                # Populate dict with new records
                data = {
                    product.id: {
                        'product_id': product.id,
                        'month': month,
                        'year': year,
                        'forecast': forecast,
                    }
                }
                for x, y in data.items():
                    data_id = self.search([('product_id', '=', y['product_id']),
                                           ('month', '=', y['month']),
                                           ('year', '=', y['year'])])
                    if data_id:
                        data_id.write(y)
                    else:
                        self.create(y)

                # Registry in monthly BoM forecast
                for bom in product.bom_ids:
                    qty = bom.product_qty
                    # Get bom_lines and compute one by one
                    for bom_line in bom.bom_line_ids:
                        line_qty = bom_line.product_qty
                        # Search for existent summary line
                        summary = self.search([
                            ('product_id', '=', bom_line.product_id.id),
                            ('year', '=', year),
                            ('month', '=', month)])
                        # Transform line_qty to forecast
                        raw_forecast = (line_qty * forecast) / qty
                        if summary:
                            for summary_line in summary:
                                for forecast_summary in summary_line.forecast_summary_ids:
                                    # If exist one ProductForecastSummary line
                                    # for the computed product
                                    if product.id == forecast_summary.mrp_product_id.id:
                                        summary_line.forecast -= forecast_summary.mrp_product_qty
                                        forecast_summary.mrp_product_qty = raw_forecast
                                        summary_line.forecast += raw_forecast
                        # If doesn't exist a summary line create new one
                        else:
                            summary_data = {
                                'product_id': bom_line.product_id.id,
                                'month': month,
                                'year': year,
                                'forecast': raw_forecast,
                            }
                            summary = self.create(summary_data)
                            forecast_summary_data = {
                                'summary_line_id': summary.id,
                                'mrp_product_id': product.id,
                                'mrp_product_qty': raw_forecast,
                            }
                            self.env['product.forecast.summary'].create(
                                forecast_summary_data)

                # Go to the Next month
                year = year if month != 12 else year + 1
                month = month + 1 if month != 12 else 1

    @api.model
    def get_time_series_forecast(self, month, year, forecast_periods, product_ids=None, grow_percent=0.0):
        """
        Compute mobile average
        :param month:
        :param year:
        :param forecast_periods:
        :param product_ids:
        :param grow_percent:
        :return:
        """

        today = datetime.today()
        month = month or today.month
        year = year or today.year

        for product in product_ids:
            current_month = month
            current_year = year
            for period in range(forecast_periods):
                # 1) Get historical
                forecast = 0.0
                # Control month number not > 12
                year = year if month != 12 else year + 1
                month = month + 1 if month != 12 else 1
                forecast_month = current_month + period
                query_year = current_year - 1 if forecast_month <= 12 else current_year
                forecast_year = current_year if forecast_month <= 12 else current_year + 1
                forecast_month = forecast_month if forecast_month <= 12 else forecast_month - 12

                query = "SELECT product_id, sum(qty) FROM view_product_summary "\
                        "WHERE doc_type != 'in_invoice' AND (month = %s AND year = %s) "\
                        "AND product_id = %s "\
                        "GROUP BY product_id, doc_type" % (
                            forecast_month, query_year, product.id)

                self._cr.execute(query)
                line = self._cr.fetchone()

                # 2) Grow historical
                if line:
                    forecast = line[1] + (line[1] * grow_percent) / 100

                # Populate dict with new records
                data = {
                    product.id: {
                        'product_id': product.id,
                        'month': forecast_month,
                        'year': forecast_year,
                        'forecast': forecast,
                    }
                }
                # 3) Write forecast
                for x, y in data.items():
                    data_id = self.search([('product_id', '=', y['product_id']),
                                           ('month', '=', y['month']),
                                           ('year', '=', y['year'])])
                    if data_id:
                        data_id.write(y)
                    else:
                        self.create(y)

                # 4) Process BoM forecast summary qty's
                # Registry in monthly BoM forecast
                for bom in product.bom_ids:
                    qty = bom.product_qty
                    # Get bom_lines and compute one by one
                    for bom_line in bom.bom_line_ids:
                        line_qty = bom_line.product_qty
                        # Search for existent summary line
                        summary = self.search([
                            ('product_id', '=', bom_line.product_id.id),
                            ('year', '=', forecast_year),
                            ('month', '=', forecast_month)])
                        # Transform line_qty to forecast
                        raw_forecast = (line_qty * forecast) / qty
                        if summary:
                            for summary_line in summary:
                                for forecast_summary in summary_line.forecast_summary_ids:
                                    # If exist one ProductForecastSummary line
                                    # for the computed product
                                    if product.id == forecast_summary.mrp_product_id.id:
                                        summary_line.forecast -= forecast_summary.mrp_product_qty
                                        forecast_summary.mrp_product_qty = raw_forecast
                                        summary_line.forecast += raw_forecast
                        # If doesn't exist a summary line create new one
                        else:
                            summary_data = {
                                'product_id': bom_line.product_id.id,
                                'month': forecast_month,
                                'year': forecast_year,
                                'forecast': raw_forecast,
                            }
                            summary = self.create(summary_data)
                            forecast_summary_data = {
                                'summary_line_id': summary.id,
                                'mrp_product_id': product.id,
                                'mrp_product_qty': raw_forecast,
                            }
                            self.env['product.forecast.summary'].create(
                                forecast_summary_data)


class ProductForecastSummary(models.Model):
    """
    Model to register MRP products & qty included in raw material
    """
    _name = 'product.forecast.summary'
    _description = __doc__

    summary_line_id = fields.Many2one(
        'product.summary', 'Product summary line')
    mrp_product_id = fields.Many2one('product.product', 'Product MRP')
    mrp_product_qty = fields.Float('Required raw qty for Product MRP')
