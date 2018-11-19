# -*- coding: utf-8 -*-
{
    'name': "Account invoice custom cc",
    'summary': """Allow define custom partners to send cc on invoice emails""",
    'version': '9.0.1.0.0',
    'author': "Fabrica de Software Libre, Odoo Community Association (OCA)",
    'maintainer': 'FSLIBRE',
    'website': 'http://www.fslibre.com',
    'license': 'AGPL-3',
    'category': 'Mail',
    'depends': [
        'account',
        'base',
        'base_mail_custom_cc',
        'mail',
    ],
    'data': [
    ],
    'demo': [],
    'test': [],
    'installable': True,
}
