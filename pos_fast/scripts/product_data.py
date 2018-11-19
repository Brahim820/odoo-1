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
    vals = {
        'list_price': 10.0,
        'description': u'description',
        'display_name': 'Product - %s' % str(i),
        'name': 'Product Eg : %s' % str(i),
        'pos_categ_id': 2,
        'to_weight': u'True',
    }
    with open("img.png", "rb") as f:
        data = f.read()
        vals['image'] = data.encode("base64")
    models.execute_kw(database, uid, password, 'product.product', 'create', [vals])