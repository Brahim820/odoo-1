# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name" : "Compute price including by products",
    "version" : "9.0.0.1",
    "depends" : [
        "product_extended",
        'mrp_byproduct',
        'product_default_bom',
    ],
    "category" : "Manufacturing",

    "init_xml" : [],
    "demo_xml" : [],
    "data" : [
        'views/mrp_byproduct.xml',
    ],
    "active": False,
    "installable": True
}
