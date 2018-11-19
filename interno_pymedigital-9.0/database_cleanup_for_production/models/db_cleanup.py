# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api

class Wizard(models.TransientModel):
    _name = "database_cleanup_for_production.wizard"
    _description = "Cleans database to use on production."

    date_from = fields.Date('Date from', )
    date_to = fields.Date('Date to', )

    limit = fields.Integer('Limit records', )

    """
    cleanup_sale_invoices = fields.Boolean(string="Clean up sale invoices", )
    sale_journal_ids = fields.Many2many(
        'account.journal', 'database_cleanup_for_production_sale_journal_rel',
        'account_id', 'journal_id', string='Journals',
        domain=[('type', '=', 'sale')], )

    cleanup_purchase_invoices = fields.Boolean(string="Clean up purchase invoices", )
    purchase_journal_ids = fields.Many2many(
        'account.journal', 'database_cleanup_for_production_purchase_journal_rel',
        'account_id', 'journal_id', string='Journals',
        domain=[('type', '=', 'purchase')], )

    inv_state = fields.Selection([
            ('draft','Draft'),
            ('proforma', 'Pro-forma'),
            ('proforma2', 'Pro-forma'),
            ('open', 'Open'),
            ('paid', 'Paid'),
            ('cancel', 'Cancelled'),
        ], string='Status', copy=False, )


    cleanup_outbound_payments = fields.Boolean(string="Clean up outbound payments", )
    cleanup_transfer_payments = fields.Boolean(string="Clean up internal transfers", )
    cleanup_inbound_payments = fields.Boolean(string="Clean up inbound payments", )
    """

    cleanup_pos_sessions = fields.Boolean(string="Clean up pos sessions", )
    cleanup_pos_orders = fields.Boolean(string="Clean up pos orders", )

#    cleanup_mrp_productions = fields.Boolean(string="Clean up MRP Productions", )
#    production_state = fields.Selection([
#        ('draft', 'New'),
#        ('cancel', 'Cancelled'),
#        ('confirmed', 'Awaiting Raw Materials'),
#        ('ready', 'Ready to Produce'),
#        ('in_production', 'Production Started'),
#        ('done', 'Done')],
#        string='Status', )

    """
    @api.multi
    def button_update_jounals(self):
        journals = self.env['account.journal'].search([])
        journals.write({'update_posted': True})

    """

    @api.multi
    def button_cleanup(self):
        for r in self:

            """
            statements = self.env['account.bank.statement'].search([])
            if r.limit:
                limit = int(r.limit)
                statements = statements[0:limit]
            for bs in statements:
                bs.clean_up_for_production()
            """

            if r.cleanup_pos_orders:
                pos_orders = self.env['pos.order'].search([])
                if r.limit:
                    limit = int(r.limit)
                    pos_orders = pos_orders[0:limit]

                for po in pos_orders:
                    if po.state != 'draft':
                        po.write({'state': 'draft'})
                    po.unlink()

            if r.cleanup_pos_sessions:
                pos_sessions = self.env['pos.session'].search([])
                if r.limit:
                    limit = int(r.limit)
                    pos_sessions = pos_sessions[0:limit]

                for ps in pos_sessions:
                    if ps.state != 'draft':
                        ps.write({'state': 'draft'})
                    ps.unlink()


            """
            # PAYMENTS (account.payment).
            payments = self.env['account.payment']
            print 'PAYMENTS', payments
            if r.cleanup_outbound_payments or r.cleanup_inbound_payments or r.cleanup_transfer_payments:
                if r.cleanup_outbound_payments:
                    payments += self.env['account.payment'].search([('payment_type', '=', 'outbound')])
                    print 'OUTBOUND', payments
                if r.cleanup_inbound_payments:
                    payments += self.env['account.payment'].search([('payment_type', '=', 'inbound')])
                    print 'INBOUND', payments
                if r.cleanup_transfer_payments:
                    payments += self.env['account.payment'].search([('payment_type', '=', 'transfer')])
                    print 'TRANSFER', payments

                for p in payments:
                    for line in p.move_line_ids:
                        line.remove_move_reconcile()
                    p.cancel()
                    p.unlink()

            # INVOICES (account.invoice).
            journals = self.env['account.journal']

            if r.cleanup_sale_invoices:
                if r.sale_journal_ids:
                    journals += r.sale_journal_ids
                else:
                    journals += self.env['account.journal'].search([('type', '=', 'sale')])

            if r.cleanup_purchase_invoices:
                if r.purchase_journal_ids:
                    journals += r.purchase_journal_ids
                else:
                    journals += self.env['account.journal'].search([('type', '=', 'purchase')])

            invoices = self.env['account.invoice']
            for j in journals:
                invoices += self.env['account.invoice'].search([('journal_id', '=', j.id)])

            # Apply filters and limits.
            if r.date_from:
                invoices = invoices.filtered(lambda i: i.date >= r.date_from)
            if r.date_to:
                invoices = invoices.filtered(lambda i: i.date <= r.date_to)
            if r.inv_state:
                invoices = invoices.filtered(lambda i: i.state == r.inv_state)
            if r.limit:
                limit = int(r.limit)
                invoices = invoices[0:limit]

            for inv in invoices:
                inv.clean_up_for_production()

            moves = self.env['account.move'].search([])
            if r.limit:
                limit = int(r.limit)
                moves = moves[0:limit]
            for move in moves:
                move.clean_up_for_production()




            # PRODUCTIONS (mrp.production)
            productions = self.env['mrp.production'].search([])

            # Apply filters and limits.
            if r.date_from:
                productions = productions.filtered(lambda p: p.date >= r.date_from)
            if r.date_to:
                productions = productions.filtered(lambda p: p.date <= r.date_to)
            if r.production_state:
                productions = productions.filtered(lambda p: p.state == r.production_state)
            if r.limit:
                productions = productions[0:r.limit]

            for pro in productions:
                if pro.state != 'draft':
                    pro.sudo().write({'state': 'draft'})
                else:
                    pro.unlink()

            # STOCK MOVES (stock.move)
            moves = self.env['stock.move'].search([])

            # Apply filters and limits.
            if r.date_from:
                moves = moves.filtered(lambda m: m.date >= r.date_from)
            if r.date_to:
                moves = moves.filtered(lambda m: m.date <= r.date_to)
            if r.production_state:
                moves = moves.filtered(lambda m: m.state == r.production_state)
            if r.limit:
                moves = moves[0:r.limit]

            for mov in moves:
                if mov.state != 'draft':
                    pro.sudo().write({'state': 'draft'})
                else:
                    pro.unlink()
            """
