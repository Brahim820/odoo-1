# -*- coding: utf-8 -*-
{
    'name': "Restrict Export",

    'summary': """
        Disable export functionality for all users except specified ones.
    """,

    'description': """
Disable export functionality for all users except administrators.
The module also create a new special user group called "Export" which allows
users to export data like usual.
    """,

    'author': "Khwunchai Jaengsawang",
    'website': "https://github.com/khwunchai",

    'category': 'Extra Rights',
    'version': '1.0.0',

    'depends': ['web'],

    'data': [
        'security/security.xml',
        'views/webclient_templates.xml',
    ],
}
