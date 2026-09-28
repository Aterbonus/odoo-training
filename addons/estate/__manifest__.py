{
    "name": "Estate Training Odoo",
    "author": "aterbonus",
    "version": "20.0.1.0.0",
    "license": "Other OSI approved licence",
    "application": True,
    "depends": ["base", "mail"],
    "data": [
        "security/res_groups.xml",
        "security/ir.access.csv",
        "views/estate_property_views.xml",
        "views/estate_property_type_views.xml",
        "views/estate_property_tag_views.xml",
        "views/estate_property_offer_views.xml",
        "views/estate_menus.xml",
        "views/rest_users_views.xml"
    ],
    "demo": [
        "demo/demo.xml"
    ]
}