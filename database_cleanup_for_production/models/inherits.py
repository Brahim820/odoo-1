# -*- coding: utf-8 -*-
import logging

from openerp import models, fields, api

_logger = logging.getLogger(__name__)

"""
class AccountInvoice(models.Model):
    _inherit = ['account.invoice']

    @api.multi
    def clean_up_for_production(self):
        for inv in self:
            if inv.state != 'draft':
                if inv.payment_move_line_ids:
                    for line in inv.payment_move_line_ids:
                        line.remove_move_reconcile()
                if inv.state == 'open':
                    inv.signal_workflow('invoice_cancel')
                if inv.state == 'cancel':
                    inv.action_cancel_draft()

            if inv.state != 'draft':
                _logger.error("Fail to convert invoice %s to draft", inv.number)

            inv.write({'move_name': ''})
            inv.unlink()


class AccountMove(models.Model):
    _inherit = ['account.move']

    @api.multi
    def clean_up_for_production(self):
        for move in self:
            for line in move.line_ids:
                if line.reconciled:
                    line.remove_move_reconcile()
            if move.state != 'draft':
                move.write({'state': 'draft'})
            move.unlink()


class AccountBankStatement(models.Model):
    _inherit = ['account.bank.statement']

    @api.multi
    def clean_up_for_production(self):
        for bs in self:
            if bs.state == 'confirm':
                bs.button_cancel()
            bs.unlink()

"""