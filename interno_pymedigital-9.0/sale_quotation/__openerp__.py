# -*- coding: utf-8 -*-
{
    'name' : 'Sale Quotation',
    'version' : '9.0.0.0.1',
    'summary': 'Quotation printing',
    'author': "Fábrica de Software Libre",
    'maintainer': 'damendieta@fslibre.com',
    'website': 'http://fslibre.com',
    'sequence': 30,
    'category' : 'Sale',
    'depends' : [
        'account',
        'crm',
        'sale',
    ],
    'data': [
        'views/sale_order.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

