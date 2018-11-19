# -*- coding: utf-8 -*-
import openerp
##import netsvc
import logging
from openerp.osv import fields, osv
import openerp.tools
from openerp.tools.translate import _
from datetime import date,datetime, timedelta
import itertools
from lxml import etree
import datetime as dt

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp

import time
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv, orm
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools import float_compare
from openerp.tools.translate import _
from openerp import tools, SUPERUSER_ID
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)

class pos_config(osv.osv):
    _inherit = 'pos.config'

    _columns = {
        'partner_id': fields.many2one('res.partner','Partner'),

        }

pos_config()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
