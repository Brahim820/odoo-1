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
            ('date_due', '>=', fir),
            ('date_due', '<=', fcr)])

        self.invoice_ids = self.env['account.invoice'].search([
            ('date_invoice', '>=', fir),
            ('date_invoice', '<=', fcr)])


    @api.multi
    def get_report_data(self):

        credit_lines = self.credit_line_ids
        invoices = self.invoice_ids
        credits = credit_lines.mapped('credit_id.partner_id')
        affiliates = self.env['res.partner']

        affiliates = affiliates | invoices.mapped('partner_id')

        header = ['CÓDIGO',
                  'APELLIDOS Y NOMBRES',
                  'TTOTAL',
                  ]

        affiliates_list = []
        for a in credits:
            for c in credit_lines:
                affiliates_list.append([
                    a.code,
                    a.name,
                    c.amount_total
            ])
        data = {
                'wizard': 'credit.affiliate.report',
                'filename': self.fcr + '.xlsx',
                'sheets':[{
                        'name': self.fcr,
                        'header': [header],
                        'rows': affiliates_list,
                    },
                ]}
        return data
