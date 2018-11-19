# -*- coding: utf-8 -*-
{
    'name': "Internal Documents",
    'summary': """Gestiona los documentos internos de la empresa.""",
    'version': '9.0.1.0.0',
    'author': "Fabrica de Software Libre,Odoo Community Association (OCA)",
    'maintainer': 'Fabrica de Software Libre',
    'website': 'http://www.libre.ec',
    'license': 'AGPL-3',
    'category': 'Tools',
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'views/docs.xml',
        'reports/report_docs.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'test': [],
    'installable': True,
}
