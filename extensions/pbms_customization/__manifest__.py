{
    "name": "PBMS Customization",
    "version": "17.0.1.0.0",
    "summary": "PBMS programme, eligibility, entitlement, priority rule, and background task views and extensions",
    "description": "Refugee-targeted PBMS program definition extensions, UGX currency integration, domain filters for eligibility/entitlement/priority, and background task wizard widgets.",
    "category": "G2P",
    "license": "LGPL-3",
    "depends": [
        "g2p_pbms",
        "refugee_registry",
        "uganda_localization",
        "refugee_ui_customization",
    ],
    "data": [
        "views/program/program_view.xml",
        "views/eligibility/eligibility_rule_view.xml",
        "views/entitlement/entitlement_rule_view.xml",
        "views/priority/priority_rule_view.xml",
        "views/bgtask/bgtask_view.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
