# -*- encoding: utf-8 -*-

from openerp.osv import osv


class PaySlip(osv.osv):
    _inherit = 'hr.payslip'

    def cancel_sheet(self, cr, uid, ids, context=None):
        move_pool = self.pool.get('account.move')
        move_line_pool = self.pool.get('account.move.line')
        move_ids = []
        move_to_cancel = []
        conciled_lines = []
        for slip in self.browse(cr, uid, ids, context=context):
            if slip.move_id:
                move_ids.append(slip.move_id.id)
                if slip.move_id.state == 'posted':
                    move_to_cancel.append(slip.move_id.id)
                    for line in slip.move_id.line_ids:
                        if line.reconciled:
                            conciled_lines.append(line.id)
        for line in move_line_pool.browse(cr, uid, conciled_lines):
            line.remove_move_reconcile()
        move_pool.button_cancel(cr, uid, move_to_cancel, context=context)
        move_pool.unlink(cr, uid, move_ids, context=context)
        return super(PaySlip, self).cancel_sheet(cr, uid, ids, context=context)

