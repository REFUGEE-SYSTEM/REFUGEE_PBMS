from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class G2PRefugee(models.Model):
    _name = "g2p.refugee"
    _description = "Unified Refugee Registry"
    _inherit = ["g2p.register.refugee_individual"]
    _table = "g2p_refugee"

    # Separate relation tables to avoid collision with inherited model
    specific_need_ids = fields.Many2many(
        "g2p.refugee.specific_need",
        "g2p_refugee_specific_need_rel",
        "refugee_id",
        "specific_need_id",
        string="Specific Needs (UNHCR Codes)",
    )
    enrolled_program_ids = fields.Many2many(
        "g2p.program.definition",
        "g2p_refugee_program_rel",
        "refugee_id",
        "program_id",
        string="Enrolled Programmes",
    )

    # =========================================================================
    # Section D: Household & Family Structure (Self-Referencing Architecture)
    # =========================================================================
    case_number = fields.Char(
        string="Household / Case Number (A01)",
        index=True,
        help="UNHCR Household / Case registration number shared by family members.",
    )
    is_head_of_household = fields.Boolean(
        string="Is Head of Household?",
        default=False,
        index=True,
        help="Check if this individual is the principal applicant / household head.",
    )
    head_of_household_id = fields.Many2one(
        "g2p.refugee",
        string="Head of Household",
        index=True,
        ondelete="set null",
        help="Reference to the head of household record.",
    )
    relationship_to_head = fields.Selection(
        selection=[
            ("head", "Head of Household"),
            ("spouse", "Spouse"),
            ("child", "Child"),
            ("parent", "Parent"),
            ("sibling", "Sibling"),
            ("grandchild", "Grandchild"),
            ("grandparent", "Grandparent"),
            ("other_relative", "Other Relative"),
            ("non_relative", "Non-Relative"),
        ],
        string="Relationship to Head",
        default="head",
        help="Relationship of this individual to the principal applicant.",
    )
    household_size = fields.Integer(
        string="Household Size",
        default=1,
        help="Number of members in the household.",
    )
    household_member_ids = fields.One2many(
        "g2p.refugee",
        "head_of_household_id",
        string="Household Members",
        help="All family members linked to this head of household.",
    )

    # =========================================================================
    # Section F: Location, Settlement & Uganda Localization Attributes
    # =========================================================================
    host_district = fields.Char(
        string="Host District",
        help="Host district in Uganda (e.g. Isingiro, Yumbe, Adjumani, Kampala).",
    )
    settlement_name = fields.Char(
        string="Settlement Name",
        help="Name of refugee settlement (e.g. Nakivale, Bidibidi, Kyaka II).",
    )
    zone_cluster = fields.Char(
        string="Zone / Cluster",
        help="Zone or cluster within the settlement.",
    )
    village_block = fields.Char(
        string="Village / Block",
        help="Village or block designation.",
    )
    plot_number = fields.Char(
        string="Plot Number",
        help="Residential or agricultural plot number allocated by OPM.",
    )
    plot_size_allocated = fields.Float(
        string="Plot Size Allocated",
        help="Plot size allocated in square meters.",
    )
    location_type = fields.Selection(
        selection=[
            ("rural_settlement", "Rural Settlement"),
            ("urban", "Urban Setting"),
            ("transit", "Transit Center"),
        ],
        string="Location Type",
        default="rural_settlement",
    )
    urban_lc1_zone = fields.Char(
        string="Urban LC1 / Zone",
        help="Local Council 1 or Zone for urban refugees.",
    )
    shelter_type = fields.Selection(
        selection=[
            ("permanent", "Permanent Structure"),
            ("semi_permanent", "Semi-Permanent"),
            ("emergency_tent", "Emergency Tent"),
            ("makeshift", "Makeshift"),
        ],
        string="Shelter Type",
    )

    # Re-point recipient references to unified model
    primary_recipient_id = fields.Many2one(
        "g2p.refugee",
        string="Primary Disbursement Recipient",
        ondelete="set null",
    )
    alternate_recipient_id = fields.Many2one(
        "g2p.refugee",
        string="Alternate Disbursement Recipient",
        ondelete="set null",
    )
    caregiver_individual_id = fields.Many2one(
        "g2p.refugee",
        string="Caregiver Individual",
        ondelete="set null",
    )
