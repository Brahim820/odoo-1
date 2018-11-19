# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################

{
    'name': 'POS Multi category',
    'summary': 'POS Multi category module help us to manage our products with multiple categories.',
    'version': '1.0',
    'category': 'Point Of Sale',
    "sequence": 1,
    'description': 'POS Multi category help us to manage our product with multiple categories.'"""
POS Multi category
=====================================

Salient Features:
----------------
    
.

**Help and Support**
================
.. |icon_features| image:: pos_multi_cat/static/src/img/icon-features.png
.. |icon_support| image:: pos_multi_cat/static/src/img/icon-support.png
.. |icon_help| image:: pos_multi_cat/static/src/img/icon-help.png
 
* For DEMO           - click here ( `VIEW DEMO <http://54.251.33.126:8080/?db=POS_Extensions>`_  ) 

|icon_help| `Help <https://webkul.com/ticket/open.php>`_ |icon_support| `Support <https://webkul.com/ticket/open.php>`_ |icon_features| `Request new Feature(s) <https://webkul.com/ticket/open.php>`_ 

""",
    "author": "Webkul Software Pvt. Ltd.",
    'website': 'http://www.webkul.com',
    'data': [
        'views/pos_multi_cat_js.xml',
        'views/pos_multi_cat_view.xml',

        ],
    'depends': [
        'point_of_sale',
        ],
    'qweb': [
        
    ],
    'images': ['static/description/Banner.png'],
    "installable": True,
    "application": True,
    "auto_install": False,
    "price":  49,
    "currency": 'EUR',
   
}
