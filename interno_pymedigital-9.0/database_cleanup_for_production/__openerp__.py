# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name" : "Database Cleanup for production",
    "version" : "9.0.0.1",
    "depends" : ['account_cancel', ],
    "category" : "Server tools",

    "init_xml" : [],
    "demo_xml" : [],
    "data" : ['views/db_cleanup.xml'],
    "active": False,
    "installable": True,
}
