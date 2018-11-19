# -*- coding: utf-8 -*-
{
    'name': "MRP user custom reports",
    'summary': """Users can use their own format definitions for MRP.""",
    'version': '9.0.1.0.1',
    'author': "Fabrica de Software Libre",
    'maintainer': 'Fabrica de Software Libre',
    'website': 'http://www.fslibre.com',
    'license': 'AGPL-3',
    'category': 'MRPs',
    'depends': [
        'bi_mrp',
        'base_report_custom_format',
    ],
    'data': [
        'views/res_users.xml',
        'views/report_mrporder.xml',
        'report/mrp_report.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
