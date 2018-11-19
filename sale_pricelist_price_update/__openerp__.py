# -*- coding: utf-8 -*-
{
    'name': "Sale Order price updater.",

    'summary': """
        Update prices on a sale order when a pricelist is modified.""",
    'author': "Fabrica de Software Libre",
    'maintainer': 'Fabrica de Software Libre',
    'website': 'http://www.fslibre.com',
    'license': 'AGPL-3',
    'category': 'MRPs',
    'version': '9.0.1.0.1',
    'depends': [
        'base',
        'sale',
    ],
    'data': [
        'views/sale_order.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
