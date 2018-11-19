# -*- coding: utf-8 -*-
from openerp import api, models, fields, registry
import json
import base64
import logging
import time

_logger = logging.getLogger(__name__)

class pos_big_data(models.Model):

    _name = "pos.big.data"

    model = fields.Char('Model', required=1)
    fields_load = fields.Text('Field load', required=1)
    domain = fields.Text('Domains load', required=1)
    log = fields.Binary('Log', required=1)

    @api.model
    def api_get_data(self, model_datas):
        _logger.info('start api_get_data')
        start_time = time.time()
        results = {}
        vals = model_datas['model_datas']
        for val in vals:
            domain_pos = val['domain']
            domain = []
            for d in domain_pos:
                domain.append((d[0], d[1], d[2]))
            fields_load = val['fields']
            model = val['model']
            datas = self.search([('model', '=', model)])
            if datas:
                results[datas[0].model] = json.loads(base64.decodestring(datas[0].log).decode('utf-8'))
            else:
                records = self.env[model].search(domain)
                values = records.read(fields_load)
                self.create({
                    'model': model,
                    'fields_load': fields_load,
                    'domain': domain,
                    'log': base64.encodestring(json.dumps(values).encode('utf-8')),
                })
                results[model] = values
        _logger.info('end api_get_data  %s' % (time.time() - start_time))
        return results