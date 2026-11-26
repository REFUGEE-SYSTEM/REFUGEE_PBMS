{
    "name": "Refugee UI Customization",
    "version": "17.0.1.0.0",
    "summary": "Frontend assets, styling, and widgets for Refugee PBMS and UGX",
    "description": "Custom Owl widgets, SCSS styling, and XML templates including BenefitUnitWidget UGX support and Beneficiaries search widget.",
    "category": "G2P",
    "license": "LGPL-3",
    "depends": ["web", "g2p_pbms", "uganda_localization"],
    "assets": {
        "web.assets_backend": [
            "/refugee_ui_customization/static/src/css/registry_styles.scss",
            "/refugee_ui_customization/static/src/js/beneficiaries_widget.js",
            "/refugee_ui_customization/static/src/js/benefit_unit_widget_ugx.js",
            "/refugee_ui_customization/static/src/xml/g2p_beneficiaries_info_tpl.xml",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
