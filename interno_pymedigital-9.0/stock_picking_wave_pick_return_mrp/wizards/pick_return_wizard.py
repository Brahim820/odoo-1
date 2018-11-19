# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions, _


class MrpPickReturnWizard(models.TransientModel):
    _inherit = "mrp.pick.return.wizard"

    @api.multi
    def create_picking(self):
        wave = self.mo_id.wave_id.id
        in_picking, out_picking = super(MrpPickReturnWizard, self).create_picking()
        if in_picking:
            in_picking.update({
                'procurement_wave_id': wave,
            })
        if out_picking:
            out_picking.update({
                'procurement_wave_id': wave,
            })

    """
    # Alternative code to add the picking to the wave.
    # Just in case, delete when the module is finished.
    @api.multi
    def create_picking(self):
        wave = self.mo_id.wave_id
        picking = super(MrpCreatePickingWizard, self).create_picking()
        print picking
        if wave:
            wave.procurement_picking_ids += picking
        return picking
    """