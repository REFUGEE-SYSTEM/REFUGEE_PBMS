from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.addons.g2p_registry_type_addon.models import G2PTargetModelMapping

# Ensure G2PTargetModelMapping contains refugee mapping
if "refugee" not in G2PTargetModelMapping.MODEL_MAPPING:
    G2PTargetModelMapping.MODEL_MAPPING["refugee"] = "g2p.refugee"


class G2PProgramDefinitionRefugeeOnly(models.Model):
    _inherit = "g2p.program.definition"

    target_registry = fields.Selection(
        selection=[
            ("refugee", "Refugee Registry"),
        ],
        string="Base Registry",
        default="refugee",
        required=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Programme Currency",
        domain=[("active", "=", True)],
        default=lambda self: self.env.ref("base.UGX", raise_if_not_found=False),
        help="Currency used for this assistance programme (e.g. UGX - Ugandan Shilling).",
    )

    @api.constrains("target_registry")
    def _check_target_registry(self):
        for rec in self:
            if rec.target_registry != "refugee":
                raise ValidationError(
                    "Only 'Refugee Registry' (refugee) is supported for new or updated program configurations."
                )
