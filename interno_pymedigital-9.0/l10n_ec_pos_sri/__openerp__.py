# -*- coding: utf-8 -*-
{
    'name': "POS ECUADOR",
    'summary': """Modificaciones tributarias y contables para el POS en Ecuador.""",
    'version': '9.0.1.0.0',
    'author': "Fabrica de Software Libre,Odoo Community Association (OCA)",
    'maintainer': 'Fabrica de Software Libre',
    'website': 'http://www.libre.ec',
    'license': 'AGPL-3',
    'category': 'Tools',
    'depends': [
        'base',
        'point_of_sale',
        'l10n_ec_sri',
    ],
    'data': [
        'views/point_of_sale.xml',
    ],
    'demo': [],
    'test': [],
    'installable': False,
    'qweb': ['static/src/xml/pos.xml'],
}
