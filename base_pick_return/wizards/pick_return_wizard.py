# -*- coding: utf-8 -*-
import openerp.addons.decimal_precision as dp
from openerp import _, api, fields, models
from openerp.exceptions import Warning as UserError


class PickReturnWizard(models.TransientModel):
    _name = "pick.return.wizard"
    _description = "Create picking or return"

    origin = fields.Char("Origin", required=True)
    route_id = fields.Many2one(
        "stock.location.route",
        "Route",
        required=True,
        domain=[("pick_return_selectable", "=", True)],
    )
    location_src_id = fields.Many2one(
        "stock.location", "Source Location", domain=[("usage", "=", "internal")]
    )
    location_dest_id = fields.Many2one(
        "stock.location", "Destination location", domain=[("usage", "=", "internal")]
    )
    location_trans_id = fields.Many2one(
        "stock.location", "Transit Location", domain=[("usage", "=", "transit")]
    )
    in_picking_type_id = fields.Many2one(
        "stock.picking.type", "In picking type")
    out_picking_type_id = fields.Many2one(
        "stock.picking.type", "Out picking type")
    min_date = fields.Datetime(
        "Scheduled date", required=True, default=fields.Datetime.now()
    )
    type = fields.Selection(
        [("pick", "Pick"), ("return", "Return")], default="pick", required=True
    )
    priority = fields.Selection(
        [("0", "Not urgent"), ("1", "Normal"),
         ("2", "Urgent"), ("3", "Very urgent")],
        default="1",
        required=True,
    )
    move_type = fields.Selection(
        [("direct", "Partial"), ("one", "All at once")], default="one", required=True
    )

    @api.multi
    def _prepare_locations(self, loc_dest=None):
        type = self.type
        route = self.route_id
        if route:
            # Reset all variables.
            src = self.env["stock.location"]
            trans = self.env["stock.location"]
            dest = self.env["stock.location"]
            in_type = self.env["stock.picking.type"]
            out_type = self.env["stock.picking.type"]
            procurements = route.pull_ids.filtered(
                lambda x: x.action == "move")

            loc_dest = loc_dest or self.location_src_id

            procurement = procurements.filtered(
                lambda x: x.location_id == loc_dest)
            if not procurement:
                raise UserError(
                    _("At least one rule must match the destination location: %s.")
                    % loc_dest.name
                )
            procurement = procurement[0]

            dest = procurement.location_id
            src = procurement.location_src_id
            in_type = procurement.picking_type_id

            propagate = procurements.filtered(
                lambda x: x.location_id == procurement.location_src_id
            )
            if propagate:
                # Ensure only one rule to propagate.
                propagate = propagate[0]

                trans = propagate.location_id
                src = propagate.location_src_id
                out_type = propagate.picking_type_id

            if type == "return":
                src, dest = dest, src

                # The pickings are interchanged if type is return.
                in_return = out_type
                out_return = in_type

                # If the pickings have return types defined, use them instead.
                if out_type.sudo().return_picking_type_id:
                    in_return = out_type.sudo().return_picking_type_id
                if in_type.sudo().return_picking_type_id:
                    out_return = in_type.sudo().return_picking_type_id

                in_type = in_return
                out_type = out_return

            return dest, src, trans, out_type, in_type

    @api.multi
    def create_pick_return_lines(self, lines=None):
        for line in lines:
            self.pick_return_line_ids.create(line)

    @api.multi
    def create_picking(self):
        src = self.location_src_id
        dest = self.location_dest_id
        trans = self.location_trans_id
        moves = self.pick_return_line_ids
        if not moves:
            raise UserError(_("You need at least one move line to process"))
        out_picking = self.env["stock.picking"]
        if trans:
            name = self.sudo().out_picking_type_id.sequence_id.next_by_id()
            out_picking = out_picking.sudo().create(
                {
                    "name": name,
                    "origin": self.origin,
                    "picking_type_id": self.out_picking_type_id.id,
                    "move_type": self.move_type,
                    "priority": self.priority,
                    "location_dest_id": trans.id,
                    "location_id": src.id,
                    "min_date": self.min_date,
                }
            )
        name = self.sudo().in_picking_type_id.sequence_id.next_by_id()
        in_picking = self.env["stock.picking"]
        in_picking = in_picking.sudo().create(
            {
                "name": name,
                "origin": self.origin,
                "picking_type_id": self.in_picking_type_id.id,
                "move_type": self.move_type,
                "priority": self.priority,
                "location_dest_id": dest.id,
                "location_id": trans.id if trans else src.id,
                "min_date": self.min_date,
            }
        )
        for move in moves:
            if move.product_uom_qty > 0:
                in_move = (
                    self.env["stock.move"]
                    .sudo()
                    .create(
                        {
                            "location_id": in_picking.location_id.id,
                            "location_dest_id": in_picking.location_dest_id.id,
                            "product_id": move.product_id.id,
                            "product_uom": move.product_uom.id,
                            "product_uom_qty": move.product_uom_qty,
                            "name": _("Supply move for: ") + self.origin,
                            "state": "draft",
                            "picking_id": in_picking.id,
                            "date_expected": self.min_date,
                        }
                    )
                )
                if out_picking:
                    out_move = (
                        self.env["stock.move"]
                        .sudo()
                        .create(
                            {
                                "location_id": out_picking.location_id.id,
                                "location_dest_id": out_picking.location_dest_id.id,
                                "product_id": move.product_id.id,
                                "product_uom": move.product_uom.id,
                                "product_uom_qty": move.product_uom_qty,
                                "name": _("Supply move for: ") + self.origin,
                                "state": "draft",
                                "picking_id": out_picking.id,
                                "move_dest_id": in_move.id,
                                "date_expected": self.min_date,
                            }
                        )
                    )
        in_picking.sudo().action_confirm()
        if out_picking:
            out_picking.sudo().action_confirm()

        return in_picking, out_picking


class PickReturnWizardLine(models.TransientModel):
    _name = "pick.return.wizard.line"
    _description = "Pick return wizard line"

    product_id = fields.Many2one(
        "product.product", string="Product", required=True)
    product_uom_qty = fields.Float(
        string="Planned Quantity",
        digits=dp.get_precision("Product Unit of Measure"),
        required=True,
    )
    product_uom = fields.Many2one("product.uom", "UoM", required=True)
