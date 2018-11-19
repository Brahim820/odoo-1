# -*- coding: utf-8 -*-
{
    'name': "Event conditions",
    'summary': """Define conditions for your events participation""",
    'version': '9.0.1.0.0',
    'author': "Fabrica de Software Libre,Odoo Community Association (OCA)",
    'maintainer': 'Fabrica de Software Libre',
    'website': 'http://www.libre.ec',
    'license': 'AGPL-3',
    'category': 'Tools',
    'depends': [
        'event',
    ],
    'data': [
        'views/event.xml',
        'views/condition.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'test': [],
    'installable': True,
}
