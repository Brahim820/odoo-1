#!/usr/bin/env python
# -*- coding: utf-8 -*-

from openerp import _, api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    _defaults = {
        'name': lambda self, cr, uid, context: context.get('employee_name', False),
        'vat': lambda self, cr, uid, context: context.get('employee_identification') or context.get('employee_passport')
    }


class ResBank(models.Model):
    _inherit = 'res.bank'

    journal_id = fields.Many2one('account.journal', string=_('Journal'), domain=[(
        'type', '=', 'bank')], help=_('Accounting journal used to generate payroll payments'))


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    # @api.multi
    # def name_get(self):
    #     res = []
    #     for row in self:
    #         res.append((row.id, self.bank_id.name or '' + ' - ' + self.acc_number or ''))
    #     return res

    _defaults = {
        'partner_id': lambda self, cr, uid, ctx: ctx.get('partner_id', False),
    }
