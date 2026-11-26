{
    "name": "G2P Registry Type: Refugees",
    "version": "17.0.1.0.0",
    "category": "G2P",
    "summary": "Adds Refugee Registry support to OpenG2P PBMS",
    "author": "OpenG2P",
    "license": "LGPL-3",
    "depends": ["g2p_registry_type_addon", "g2p_pbms", "g2p_registry_addon"],
    "data": [
        "views/rule_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "g2p_registry_type_refugee/static/src/xml/g2p_beneficiaries_info_refugee.xml",
        ],
    },
    "installable": True,
    "application": False,
}
