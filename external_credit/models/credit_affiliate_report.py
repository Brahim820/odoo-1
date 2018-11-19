# -*- coding: utf-8 -*-
####################################################
# Parte del Proyecto LibreGOB: http://libregob.org #
# Licencia AGPL-v3                                 #
####################################################
import base64
import logging
from calendar import monthrange
from openerp.exceptions import UserError
import datetime

from openerp import _, api, fields, models

try:
    import openpyxl
except ImportError:
    _logger.error("The module openpyxl can't be loaded, try: pip install openpyxl")


class CreditAffiliateReport(models.Model):
    _name = 'credit.affiliate.report'
    _inherit = 'bi.abstract.report'
    _description = 'Credit Affiliate Report'

    name = fields.Char(string="Name", )
    fcr = fields.Date(string='Due date', )
    partner_ids = fields.Many2many(
        'res.partner',
        'partner_report_rel',
        'affiliate_report_ids',
        string='Partners', )
    credit_line_ids = fields.Many2many(
        'credit.credit.line',
        'credit_line_report_rel',
        'affiliate_report_ids',
        string='Credits',
         )
    invoice_ids = fields.Many2many(
        'account.invoice',
        'invoice_report_rel',
        'affiliate_report_ids',
        string='Invoices', )

    @api.multi
    @api.onchange('fcr')
    def _onchange_fcr(self):

        fcr = self.fcr
        if not fcr:
            return

        date = fields.Date.from_string(fcr)
        date_range = monthrange(date.year, date.month)
        fcr = date.replace(day=date_range[1])
        fir = date.replace(day=1)
        self.fcr = fields.Date.to_string(fcr)


        self.credit_line_ids = self.env['credit.credit.line'].search([
        #   ('date_due', '>=', fir),
            ('date_due', '<=', fcr),
            ('state', 'in', ("open", "partial")),
        ])

        self.invoice_ids = self.env['account.invoice'].search([
        #    ('date_invoice', '>=', fir),
            ('date_invoice', '<=', fcr),
            ('state', '=', 'draft'),
        ])

        self.partner_ids = self.credit_line_ids.mapped('credit_id.partner_id') \
            | self.invoice_ids.mapped('partner_id')

    @api.multi
    def get_report_data(self):
#        import wdb; wdb.set_trace()
        header_list = ['CÓDIGO',
                  'APELLIDOS Y NOMBRES',
                  'TTOTAL',
                  ]

        partner_list = []
        for partner in self.partner_ids:
            credits = partner.credit_ids
            credit_lines = credits.mapped('credit_line_ids'). \
                    filtered(lambda x: x.date_due <= self.fcr and
                             x.state in ('open', 'partial'))
            invoices = partner.invoice_ids. \
                filtered(
                    lambda x: x.state == 'draft'
                    and x.date_invoice <= self.fcr)
            total = sum(l.amount_total for l in credit_lines) + \
                sum(i.no_declarado for i in invoices)

            p_list = [partner.code, partner.name, total]
            t_list = p_list + credit_lines.mapped('amount_total') + \
                invoices.mapped('no_declarado')
            partner_list.append(t_list)

            if credits.mapped('credit_type_id.name') not in header_list:
                header_list.extend(credits.mapped('credit_type_id.name'))
            if invoices.mapped('name') not in header_list:
                header_list.extend(invoices.mapped('name'))


        data = {
                'wizard': 'credit.affiliate.report',
                'filename': self.fcr + '.xlsx',
                'sheets':[{
                        'name': self.fcr,
                        'header': [header_list],
                        'rows': partner_list,
                    },
                ]}
        return data
