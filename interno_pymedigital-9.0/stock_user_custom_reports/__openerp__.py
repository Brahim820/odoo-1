# -*- coding: utf-8 -*-
{
    'name': "Stock user custom formats",
    'summary': """Users can define their own stock formats.""",
    'version': '9.0.1.0.1',
    'author': "Fabrica de Software Libre",
    'maintainer': 'Fabrica de Software Libre',
    'website': 'http://www.fslibre.com',
    'license': 'AGPL-3',
    'category': 'Stock',
    'depends': [
        'base',
        'stock',
        'stock_inventory_discrepancy',
        'stock_inventory_communication',
        'base_report_custom_format',
    ],
    'data': [
        'views/res_users.xml',
        'views/report_stock.xml',
        'views/stock.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
