# -*- coding: utf-8 -*-
{
    'name': "BASE ELECTRONIC SIGNATURE",

    'summary': """Base to sign documents with p12 files.""",

    'external_dependencies': {'bin': ['/usr/bin/java']},

    'author': "ISISCOR, FÁBRICA DE SOFTWARE LIBRE",
    'website': 'http://www.isiscor.com, http://www.fslibre.com',
    'category': 'Tools',
    'version': '9.0.0.1',
    'maintainer': 'ISISCOR',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'report',
    ],

    'data': [
        "security/ir.model.access.csv",
        "views/electronic_signature.xml",
    ],
    'demo': [],
    'test': [],
    'installable': True,
}
