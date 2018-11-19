{
    'name': 'POS Big Datas, Fast loading POS',
    'version': '4.2',
    'category': 'Point of Sale',
    'sequence': 0,
    'author': 'TL Technology',
    'website': 'http://bruce-nguyen.com',
    'price': '150',
    'description': 'Only need 10s for loading 1,000,000 rows to POS screen',
    "currency": 'EUR',
    'depends': ['pos_product_template'],
    'data': [
        'security/ir.model.access.csv',
        'datas/auto_run.xml',
        'template/import.xml',
        'wizard/auto_cache.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'application': True,
    'images': ['static/description/icon.png'],
    'license': 'LGPL-3',
    'support': 'thanhchatvn@gmail.com'
}
