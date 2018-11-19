import xmlrpclib
import json
import time

start_time = time.time()

database = 'bruce8'
login = 'admin'
password = '1'
url = 'http://localhost:8069'

common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(database, login, password, {})


models = xmlrpclib.ServerProxy(url + '/xmlrpc/object')


for i in range(10000, 100000):

    ids = models.execute_kw(database, uid, password, 'product.product', 'search', [[['available_in_pos', '=', True]]])
    for id in ids:
        product = models.execute_kw(database, uid, password, 'product.product', 'read', [id], {'fields': ['image', 'name']})
        models.execute_kw(database, uid, password, 'product.product', 'copy', [id], {'default': {
            'image': product['image'],
            'name': product['name'] + '_' + str(i),
        }})
    ("--- %s seconds ---" % (time.time() - start_time))
    print '-' * 100


{'warranty': None, 'create_date': '2017-04-28 07:08:53.801755', 'weight': 0.0, 'sequence': 1, 'color': None, 'sale_line_warn_msg': None, 'write_uid': 1, 'uom_id': 1, 'description_purchase': None, 'default_code': None, 'list_price': 10.0, 'location_id': None, 'id': 4910, 'create_uid': 1, 'sale_ok': True, 'purchase_ok': True, 'description_picking': None, 'message_last_post': None, 'company_id': 1, 'product_tmpl_id': 4910, 'track_service': u'manual', 'uom_po_id': 1, 'type': u'consu', 'description': u'description', 'barcode': None, 'warehouse_id': None, 'volume': 0.0, 'tracking': u'none', 'write_date': '2017-04-28 07:08:53.801755', 'active': True, 'rental': False, 'sale_delay': 0.0, 'name': u'Product Example - 0', 'expense_policy': u'no', 'description_sale': None, 'available_in_pos': True, 'categ_id': 1, 'pos_categ_id': 2, 'invoice_policy': u'order', 'to_weight': True, 'sale_line_warn': u'no-message'}
