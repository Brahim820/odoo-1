# -*- coding: utf-8 -*-

import json
import openerp
from openerp.http import request
from openerp.addons.bus.controllers.main import BusController


class BusController(BusController):

    def _poll(self, dbname, channels, last, options):
        if request.session.uid:
            channels.append((request.db, 'pos_sync_session', request.uid))
        return super(BusController, self)._poll(dbname, channels, last, options)

    @openerp.http.route('/pos_sync_session', type="json", auth="public")
    def multi_session_update(self, **args):
    	session_id = args['session_id'] if args.has_key('session_id') else 0
    	order = args['order'] if args.has_key('order') else {}
        res = request.env["pos.sync.session"].browse(int(session_id)).order_operations(order)
        return res
