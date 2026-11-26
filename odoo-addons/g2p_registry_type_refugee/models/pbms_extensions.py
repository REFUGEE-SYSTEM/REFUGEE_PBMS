from odoo import fields, models


class G2PProgramDefinitionRefugee(models.Model):
    _inherit = "g2p.program.definition"

    target_registry = fields.Selection(
        selection_add=[("refugees", "Refugees")],
        ondelete={"refugees": "cascade"},
    )


class G2PEligibilityRuleDefinitionRefugee(models.Model):
    _inherit = "g2p.eligibility.rule.definition"

    target_registry = fields.Selection(
        selection_add=[("refugees", "Refugees")],
        ondelete={"refugees": "cascade"},
    )


class G2PEntitlementRuleDefinitionRefugee(models.Model):
    _inherit = "g2p.entitlement.rule.definition"

    target_registry = fields.Selection(
        selection_add=[("refugees", "Refugees")],
        ondelete={"refugees": "cascade"},
    )


class G2PPriorityRuleDefinitionRefugee(models.Model):
    _inherit = "g2p.priority.rule.definition"

    target_registry = fields.Selection(
        selection_add=[("refugees", "Refugees")],
        ondelete={"refugees": "cascade"},
    )
