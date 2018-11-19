# -*- coding: utf-8 -*-
{
    'name': "Product Summary and Forecast",
    'summary': """Inventory Summary in purchases, sales and production""",
    'description': """Inventory Summary in purchases, sales and production""",
    'version': '9.0.1.0.0',
    'author': "Jonathan Finlay <jfinlay@riseup.net>, Edison Ibáñez <edison@disroot.org>",
    'maintainer': 'Jonathan Finlay',
    'website': '',
    'license': 'AGPL-3',
    'category': 'Warehouse',
    'depends': [
        'mrp',
        'product',
        'sale',
        'stock'
    ],
    'data': [
        'views/product_view.xml',
        'views/stock_view.xml',
        'views/resource_view.xml',
        'wizard/orderpoint_recompute_view.xml',
        'wizard/forecast_compute_view.xml',
        'wizard/product_summary_compute_view.xml',
        'data/ir_cron.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'sequence': 10,
}
