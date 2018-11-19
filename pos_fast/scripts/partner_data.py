import xmlrpclib
import json
import time

start_time = time.time()

database = 'v9_pos_fast'
login = 'admin'
password = 'admin'
url = 'http://localhost:8069'

common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(database, login, password, {})

models = xmlrpclib.ServerProxy(url + '/xmlrpc/object')

for i in range(0, 100000):
    vals = {'phone': u'False', 'street': u'89 Lingfield Tower', 'write_date': u'2016-11-29 11:13:00',
            'city': u'London', 'name': 'Customer - %s' % str(i), 'zip': u'False', 'mobile': u'0902403918',
            'country_id': 233, 'state_id': False, 'email': u'thanhchatvn@gmail.com',
            'vat': u'False'}
    models.execute_kw(database, uid, password, 'res.partner', 'create', [vals])
    ("--- %s seconds ---" % (time.time() - start_time))


