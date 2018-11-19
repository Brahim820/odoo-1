# -*- coding: utf-8 -*-
import base64
from cStringIO import StringIO

import logging
_logger = logging.getLogger(__name__)

from openerp import models, fields, api, _
from openerp.exceptions import UserError

try:
    import openpyxl
except ImportError:
    _logger.error("The module openpyxl can't be loaded, try: pip install openpyxl")

class BiSaleReport(models.TrascientModel):
    _name = 'bi.sale.report'
    _inherit = 'bi.abstract.report'
    _description = 'Bi Sale Report'

    @api.multi
    def get_report_data(self):

        """
        return: diccionario con:
        data = {
            'wizard': 'nombre.del.wizard',
            'filename': 'archivo.xlsx',
            'sheets':[
                {
                'name': 'nombre',
                'rows': [[A,B,C],[1,2,3],[4,5,6]]
                }
                {
                'name': 'nombre',
                'rows': [[A,B,C],[1,2,3],[4,5,6]]
                }
        """
        return False

