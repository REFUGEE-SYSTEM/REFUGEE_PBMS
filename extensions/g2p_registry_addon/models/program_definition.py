from odoo import fields, models


class G2PProgramDefinitionRefugeeOnly(models.Model):
    _inherit = "g2p.program.definition"

    target_registry = fields.Selection(
        selection=[
            ("refugee_individual", "Refugee Individual"),
            ("refugee_group", "Refugee Group"),
        ],
        string="Target Registry",
        required=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Programme Currency",
        domain=[("active", "=", True)],
        default=lambda self: self.env.ref("base.UGX", raise_if_not_found=False),
        help="Currency used for this assistance programme (e.g. UGX - Ugandan Shilling).",
    )
