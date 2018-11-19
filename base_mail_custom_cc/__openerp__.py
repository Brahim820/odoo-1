# -*- coding: utf-8 -*-
{
    'name': "Base mail custom cc",
    'summary': """Allow define a custom partners to send cc on emails""",
    'version': '9.0.1.0.0',
    'author': "Fabrica de Software Libre, Odoo Community Association (OCA)",
    'maintainer': 'FSLIBRE',
    'website': 'http://www.fslibre.com',
    'license': 'AGPL-3',
    'category': 'Mail',
    'depends': [
        'base',
        'mail',
        'itis_mail_cc_bcc',
    ],
    'data': [
    ],
    'demo': [],
    'test': [],
    'installable': True,
}
