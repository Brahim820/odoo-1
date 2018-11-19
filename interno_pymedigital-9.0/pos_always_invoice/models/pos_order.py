from datetime import datetime
import logging
from openerp import SUPERUSER_ID
from openerp import api
from openerp import models
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.v7
    def create_from_ui(self, cr, uid, orders, context=None):
        for order in orders :
            if order[u'data'][u'partner_id']:
                order[u'to_invoice'] = True
        result= super(PosOrder,self).create_from_ui(cr, uid, orders, context=context)
        return result
