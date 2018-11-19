import xmlrpclib
import time

start_time = time.time()

database = 'bruce8'
login = 'admin'
password = '1'
url = 'http://localhost:8069'

common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(database, login, password, {})


models = xmlrpclib.ServerProxy(url + '/xmlrpc/object')

models.execute_kw(database, uid, password, 'pos.auto.cache', 'auto_cache', [])
("--- %s seconds ---" % (time.time() - start_time))
print '-' * 100