# -*- coding: utf-8 -*-
from openerp import api, models, fields, registry
import logging
import base64
import json

_logger = logging.getLogger(__name__)

class pos_auto_cache(models.TransientModel):

    _name = "pos.auto.cache"

    @api.model
    def auto_clean_cache(self):
        self.clear_cache()
        return True

    @api.multi
    def clear_cache(self):
        _logger.info('begin clear_cache')
        caches = self.env['pos.big.data'].search([])
        _logger.info('len cache: %s' % len(caches))
        for cache in caches:
            model = cache.model
            fields_load = cache.fields_load
            records = self.env[model].search(eval(cache.domain))
            values = records.read(eval(fields_load))
            cache.write({
                'log': base64.encodestring(json.dumps(values).encode('utf-8')),
            })
        _logger.info('end clear_cache')
        return True


