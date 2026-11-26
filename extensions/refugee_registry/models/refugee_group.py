from odoo import models, fields, api
from odoo.exceptions import ValidationError

from .registry import G2PRegistry


class G2PRefugeeGroupRegistry(models.Model):
    _name = "g2p.register.refugee_group"
    _description = "Refugee Group / Household Registry"
    _inherit = "g2p.registry"
    _rec_name = "record_name"

    # Base Registry Fields
    functional_record_id = fields.Char(string="Functional Record ID", index=True)
    link_internal_record_id = fields.Char(string="Link Internal Record ID", index=True)
    record_name = fields.Char(string="Group Name / Number", compute="_compute_record_name", store=True)
    record_status = fields.Selection(
        selection=[
            ("active", "Active"),
            ("inactive", "Inactive"),
            ("suspended", "Suspended"),
            ("closed", "Closed"),
            ("archived", "Archived"),
        ],
        string="Record Status (Q01)",
        default="active",
        required=True,
    )
    record_status_reason = fields.Char(string="Record Status Reason")

    # =========================================================================
    # [CATEGORY A] Case & Registration Record Attributes
    # =========================================================================

    # [A01] Household / Case Number - Text / Identifier
    case_number = fields.Char(
        string="Household / Case Number (A01)",
        index=True,
        help="Primary household registration / case number (e.g. UNHCR manifest case number).",
    )

    # [A02] Registration Date - Date
    registration_date = fields.Date(
        string="Registration Date (A02)",
        help="Date when the household registration was conducted.",
    )

    # [A04] Point of Entry / Reception Centre - Selection / Text
    point_of_entry = fields.Char(
        string="Point of Entry / Reception Centre (A04)",
        help="Border entry post or transit/reception centre (e.g., Elegu, Busia, Nyakabande, Kisoro). Pending gazetted code list.",
    )

    # [A05] Registration Site / Office - Selection / Text
    registration_site = fields.Char(
        string="Registration Site / Office (A05)",
        help="Field office or registration desk where household enrolment took place.",
    )

    # [A06] Registering Officer ID - Text
    registering_officer_id = fields.Char(
        string="Registering Officer ID (A06)",
        help="Official identifier or staff code of the registering officer.",
    )

    # =========================================================================
    # [CATEGORY F] Household Composition Attributes (F01, F03-F06, F08)
    # =========================================================================

    # [F01] Head of Household / Principal Applicant (Reference to individual refugee)
    head_of_household_id = fields.Many2one(
        "g2p.register.refugee_individual",
        string="Head of Household / Principal Applicant (F01)",
        index=True,
    )
    head_of_household_internal_record_id = fields.Char(
        string="Head of Household Internal Record ID",
        index=True,
        compute="_compute_head_internal_id",
        store=True,
        readonly=False,
    )
    household_head_name = fields.Char(
        string="Household Head Name",
        compute="_compute_head_name",
        store=True,
    )

    # Member links (logical relationship between household and individual refugees)
    member_ids = fields.One2many(
        "g2p.refugee.group.member",
        "group_id",
        string="Household Members",
    )

    # [F03] Household Size - Calculated number (Integer)
    household_size = fields.Integer(
        string="Household Size (F03)",
        compute="_compute_household_composition",
        store=True,
    )

    # [F04] Dependency Ratio - Calculated number (Decimal)
    # Proposed demographic thresholds: Dependents (<15 or >=65) / Working-age (15-64).
    # NOTE: Thresholds remain provisional pending formal project-owner approval.
    dependency_ratio = fields.Float(
        string="Dependency Ratio Numeric (F04)",
        compute="_compute_household_composition",
        digits=(6, 2),
        store=True,
    )
    dependency_ratio_display = fields.Char(
        string="Dependency Ratio (F04)",
        compute="_compute_household_composition",
        store=True,
        help="Dependency ratio display with safe N/A handling when zero working-age members exist.",
    )
    dependency_ratio_status = fields.Selection(
        selection=[
            ("calculated", "Calculated"),
            ("zero_working_age", "N/A - Zero Working-Age Members"),
            ("no_members", "N/A - No Members"),
        ],
        string="Dependency Ratio Status",
        compute="_compute_household_composition",
        store=True,
    )

    # [F05] Female-headed Household - Calculated Boolean
    female_headed_household = fields.Boolean(
        string="Female-headed Household (F05)",
        compute="_compute_household_composition",
        store=True,
    )

    # [F06] Child-headed Household - Calculated Boolean
    child_headed_household = fields.Boolean(
        string="Child-headed Household (F06)",
        compute="_compute_household_composition",
        store=True,
    )

    # [F08] Family Members Left Behind / Separated - Count & Notes
    members_left_behind_count = fields.Integer(
        string="Members Left Behind Count (F08)",
        default=0,
        help="Number of direct household members separated or remaining in country of origin.",
    )
    members_left_behind_notes = fields.Text(
        string="Members Left Behind Notes (F08)",
        help="Details on whereabouts, separation circumstances, or tracing requirements.",
    )

    # =========================================================================
    # [CATEGORY G] Location & Settlement Attributes (G01 - G09)
    # =========================================================================

    # [G01] Host District - Char / Selection
    host_district = fields.Char(
        string="Host District (G01)",
        index=True,
        help="Host government administrative district (e.g. Isingiro, Kyegegwa, Yumbe, Adjumani, Kampala).",
    )

    # [G02] Settlement or Urban Location - Selection & Settlement Name
    location_type = fields.Selection(
        selection=[
            ("settlement", "Refugee Settlement"),
            ("urban", "Urban / Non-Settlement Area"),
        ],
        string="Location Type (G02)",
        default="settlement",
        help="Classification of dwelling location: gazetted refugee settlement or urban setting.",
    )
    settlement_name = fields.Char(
        string="Settlement / Area Name (G02)",
        help="Name of refugee settlement (e.g., Nakivale, Kyaka II, Bidibidi, Rhino Camp) or urban division.",
    )

    # [G03] Zone / Cluster - Char
    zone_cluster = fields.Char(
        string="Zone / Cluster (G03)",
        help="Administrative zone or cluster within the settlement.",
    )

    # [G04] Village / Block - Char
    village_block = fields.Char(
        string="Village / Block (G04)",
        help="Village or block identifier within the zone.",
    )

    # [G05] Plot Number - Char
    plot_number = fields.Char(
        string="Plot Number (G05)",
        help="Designated residential/agricultural plot number.",
    )

    # [G06] Plot Size Allocated - Float (Measured in Square Metres)
    plot_size_allocated = fields.Float(
        string="Plot Size Allocated (G06)",
        digits=(6, 2),
        help="Allocated plot size measured in Square Metres (m²). Standard OPM/UNHCR residential and agricultural plot allocation (e.g. 30x30m = 900 m², 50x50m = 2500 m²).",
    )

    # [G07] GPS Coordinates of Dwelling - Latitude & Longitude
    latitude = fields.Char(string="Latitude (G07)", help="GPS Latitude coordinate of dwelling.")
    longitude = fields.Char(string="Longitude (G07)", help="GPS Longitude coordinate of dwelling.")

    # [G08] Urban Address & LC1 - Address Lines & Local Council 1
    address_line_1 = fields.Char(string="Address Line 1 (G08)")
    address_line_2 = fields.Char(string="Address Line 2 (G08)")
    urban_lc1_zone = fields.Char(
        string="Urban LC1 / Zone (G08)",
        help="Local Council 1 (LC1) zone or cell designation for urban residences.",
    )
    country_code = fields.Char(string="Country Code", index=True, default="UGA")

    # [G09] Date of Relocation to Settlement - Date
    relocation_date = fields.Date(
        string="Relocation Date (G09)",
        help="Date when the household was relocated to or settled in the current location.",
    )

    # =========================================================================
    # [CATEGORY L] Livelihood and Economic Profile (L01 - L05, L08)
    # =========================================================================

    # [L01] Main Source(s) of Income - Multi-select
    income_sources = fields.Json(
        string="Main Income Sources (L01)",
        default=list,
        help="Household income sources. Allowed values: Farming, Casual labour, Business, Salary, Remittances, Aid only, None.",
    )
    income_sources_display = fields.Char(
        string="Income Sources Display",
        compute="_compute_income_sources_display",
        store=True,
    )

    # [L02] Number of Working-Age Members Earning Income
    working_age_earners_count = fields.Integer(
        string="Working-Age Earners Count (L02)",
        default=0,
        help="Number of household members in the working-age group (15–64) who earn income.",
    )

    # [L03] Access to Cultivable Land - Selection
    cultivable_land_access = fields.Selection(
        selection=[
            ("own_plot", "Own plot"),
            ("rented_borrowed", "Rented / borrowed"),
            ("none", "None"),
        ],
        string="Access to Cultivable Land (L03)",
        help="Household access to agricultural cultivable land.",
    )

    # [L04] Productive Assets & Livestock - Multi-select
    productive_assets = fields.Json(
        string="Productive Assets & Livestock (L04)",
        default=list,
        help="Household productive assets: Hoe, Bicycle, Phone, Livestock, Sewing machine, Solar, None.",
    )
    productive_assets_display = fields.Char(
        string="Productive Assets Display",
        compute="_compute_productive_assets_display",
        store=True,
    )

    # [L05] Shelter Type & Condition - Selection
    shelter_type = fields.Selection(
        selection=[
            ("tent_tarpaulin", "Tent / tarpaulin"),
            ("mud_thatch", "Mud and thatch"),
            ("semi_permanent", "Semi-permanent"),
            ("permanent", "Permanent"),
        ],
        string="Shelter Type (L05)",
        help="Primary dwelling structure type and condition.",
    )

    # [L08] Monthly Household Income (approx.) - Monetary / UGX
    monthly_household_income = fields.Float(
        string="Monthly Household Income in UGX (L08)",
        digits=(12, 2),
        groups="g2p_pbms.group_program_super_administration,base.group_erp_manager",
        help="Estimated total monthly household cash income in Uganda Shillings (UGX). Special protected economic data.",
    )

    # =========================================================================
    # [CATEGORY M] Targeting, Vulnerability & Programme Enrolment (M01 - M06)
    # =========================================================================

    # [M01] Assistance Category - Selection (Marked Provisional)
    assistance_category = fields.Selection(
        selection=[
            ("cat_1", "Category 1 – High Vulnerability / Full Assistance (Provisional)"),
            ("cat_2", "Category 2 – Moderate Vulnerability / Partial Assistance (Provisional)"),
            ("cat_3", "Category 3 – Low Vulnerability / Self-Reliant (Provisional)"),
            ("pending", "Pending Assessment"),
        ],
        string="Assistance Category (M01)",
        default="pending",
        help="Approved social assistance vulnerability category (Provisional pending official gazetting).",
    )

    # [M02] Vulnerability Score - Float (0-100) & Methodology Status
    vulnerability_score = fields.Float(
        string="Vulnerability Score (M02)",
        digits=(5, 2),
        help="Calculated vulnerability score (0 to 100). Note: Score is auditable once official methodology is approved.",
    )
    vulnerability_score_status = fields.Selection(
        selection=[
            ("pending_methodology", "Pending Methodology Approval"),
            ("calculated", "Calculated"),
            ("exempt", "Exempt"),
        ],
        string="Vulnerability Score Status (M02)",
        default="pending_methodology",
        help="Status of vulnerability scoring methodology.",
    )

    # [M03] New-Arrival Status & End Date
    is_new_arrival = fields.Selection(
        selection=[("yes", "Yes"), ("no", "No")],
        string="New-Arrival Status (M03)",
        default="no",
        help="Indicates whether the refugee household is classified as a new arrival.",
    )
    new_arrival_end_date = fields.Date(
        string="New-Arrival End Date (M03)",
        help="Expiry date for new-arrival status / transitional assistance.",
    )

    # [M04] Programmes Enrolled - PBMS Native Programme Membership
    enrolled_program_ids = fields.Many2many(
        "g2p.program.definition",
        "g2p_refugee_grp_program_rel",
        "group_id",
        "program_id",
        string="Enrolled Programmes (M04)",
        help="Active PBMS social protection programmes in which the household is enrolled.",
    )

    # [M05] Enrolment / Exit Date and Reason
    enrolment_date = fields.Date(
        string="Programme Enrolment Date (M05)",
        help="Date when the household was enrolled in PBMS assistance.",
    )
    exit_date = fields.Date(
        string="Programme Exit Date (M05)",
        help="Date when the household exited the programme.",
    )
    exit_reason = fields.Selection(
        selection=[
            ("graduated", "Graduated"),
            ("relocated", "Relocated"),
            ("repatriated", "Repatriated"),
            ("resettled", "Resettled"),
            ("deceased", "Deceased"),
            ("inactive", "Inactive"),
            ("ineligible", "Ineligible"),
        ],
        string="Exit Reason (M05)",
        help="Reason for programme exit/closure according to data dictionary standard categories.",
    )

    # [M06] Appeal Category - Selection & Date
    appeal_category = fields.Selection(
        selection=[
            ("no", "No"),
            ("pending", "Pending"),
            ("upheld", "Upheld"),
            ("rejected", "Rejected"),
        ],
        string="Appeal of Categorisation (M06)",
        default="no",
        help="Status of appeal against assigned assistance category.",
    )
    appeal_date = fields.Date(
        string="Appeal Date (M06)",
        help="Date when categorisation appeal was submitted.",
    )

    # =========================================================================
    # [CATEGORY N] Assistance Delivery and Entitlement (N01 - N09)
    # =========================================================================

    # [N01] Delivery Modality - Selection
    delivery_modality = fields.Selection(
        selection=[
            ("cash", "Cash"),
            ("in_kind_food", "In-kind Food"),
            ("voucher", "Voucher"),
            ("mixed", "Mixed"),
        ],
        string="Delivery Modality (N01)",
        help="Household assistance delivery mechanism modality.",
    )

    # [N02] Cash Delivery Mechanism - Selection
    cash_delivery_mechanism = fields.Selection(
        selection=[
            ("mobile_money", "Mobile Money"),
            ("agency_banking", "Agency Banking / Bank Account"),
            ("cash_in_hand", "Cash in Hand"),
        ],
        string="Cash Delivery Mechanism (N02)",
        help="Delivery mechanism for cash transfers.",
    )

    # [N03] Financial Service Provider - Text / Reference
    financial_service_provider = fields.Char(
        string="Financial Service Provider (N03)",
        help="FSP designated for assistance disbursement (e.g. MTN Uganda, Airtel Money, PostBank, Centenary Bank).",
    )

    # [N04] Account / Mobile Money Number - Protected Text
    account_number = fields.Char(
        string="Account / Mobile Money Number (N04)",
        groups="g2p_pbms.group_program_super_administration,base.group_erp_manager",
        help="Bank account or mobile money telephone number for payment delivery. Protected financial data.",
    )
    account_number_masked = fields.Char(
        string="Account Number (Masked)",
        compute="_compute_account_number_masked",
        store=True,
        help="Masked account or mobile money number for general viewing.",
    )

    # [N05] KYC Match - Selection
    kyc_match = fields.Selection(
        selection=[
            ("yes", "Yes"),
            ("no", "No"),
            ("pending", "Pending"),
        ],
        string="KYC Match (N05)",
        default="pending",
        help="Indicates whether recipient identity matches FSP KYC customer records.",
    )

    # [N06] Primary Recipient - Reference to Individual Refugee
    primary_recipient_id = fields.Many2one(
        "g2p.register.refugee_individual",
        string="Primary Recipient (N06)",
        help="Designated primary payment recipient for the household.",
    )

    # [N07] Alternate Recipient / Proxy - Reference to Individual Refugee
    alternate_recipient_id = fields.Many2one(
        "g2p.register.refugee_individual",
        string="Alternate Recipient / Proxy (N07)",
        help="Designated alternate recipient or payment collection proxy.",
    )

    # [N08] Distribution / Cash-out Point - Text / Location
    distribution_point = fields.Char(
        string="Distribution / Cash-out Point (N08)",
        help="Food distribution point (FDP) or cash-out agent location.",
    )

    # [N09] Entitlement Amount - Monetary / Float
    entitlement_amount = fields.Float(
        string="Entitlement Amount in UGX (N09)",
        digits=(12, 2),
        help="Approved household entitlement disbursement amount in Uganda Shillings (UGX).",
    )

    # =========================================================================
    # [CATEGORY O] Payment and Post-Distribution Monitoring (O01 - O05)
    # =========================================================================

    # [O01] Payment Cycle - YYYY-MM Format
    payment_cycle = fields.Char(
        string="Payment Cycle (O01)",
        help="Payment disbursement cycle in YYYY-MM format (e.g. 2024-11).",
    )

    # [O02] Authentication Method / Result - Selection
    authentication_method_result = fields.Selection(
        selection=[
            ("fingerprint_ok", "Fingerprint OK"),
            ("iris_ok", "Iris OK"),
            ("manual_override", "Manual Override"),
            ("failed", "Failed"),
        ],
        string="Authentication Method / Result (O02)",
        help="Authentication method and verification outcome at assistance collection.",
    )

    # [O03] Payment Status - Selection
    payment_status = fields.Selection(
        selection=[
            ("sent", "Sent"),
            ("credited", "Credited"),
            ("collected", "Collected"),
            ("failed", "Failed"),
            ("reversed", "Reversed"),
            ("returned", "Returned"),
            ("not_collected", "Not Collected"),
            ("unreconciled", "Unreconciled"),
        ],
        string="Payment Status (O03)",
        help="Status of assistance disbursement transaction.",
    )

    # [O04] Transaction Reference & Date
    transaction_reference = fields.Char(
        string="Transaction Reference (O04)",
        help="External transaction reference or payment voucher code.",
    )
    transaction_date = fields.Date(
        string="Transaction Date (O04)",
        help="Date when the payment was executed or collection recorded.",
    )

    # [O05] Post-Distribution Monitoring (PDM) Sample Flag - Selection
    is_pdm_sample = fields.Selection(
        selection=[
            ("yes", "Yes"),
            ("no", "No"),
        ],
        string="PDM Sample Flag (O05)",
        default="no",
        help="Indicates whether this household is sampled for post-distribution monitoring evaluation.",
    )

    # =========================================================================
    # [CATEGORY P] Consent, Data Sharing and Complaints (P01 - P05)
    # =========================================================================

    # [P01] Informed Consent - Selection & Date
    informed_consent = fields.Selection(
        selection=[
            ("yes", "Yes"),
            ("no", "No"),
            ("withdrawn", "Withdrawn"),
        ],
        string="Informed Consent (P01)",
        help="Informed consent obtained from household head for registration and assistance.",
    )
    consent_date = fields.Date(
        string="Consent Date (P01)",
        help="Date when informed consent was given.",
    )

    # [P02] Consent for Information Sharing - Multi-select
    consent_information_sharing = fields.Json(
        string="Consent for Info Sharing (P02)",
        default=list,
        help="Agreed information sharing recipients: OPM, UNHCR, WFP, Financial Service Providers, Implementing Partners.",
    )
    consent_sharing_display = fields.Char(
        string="Consent Sharing Display",
        compute="_compute_consent_sharing_display",
        store=True,
    )

    # [P03] Parent / Guardian Consent - Selection
    parent_guardian_consent = fields.Selection(
        selection=[
            ("yes", "Yes"),
            ("no", "No"),
        ],
        string="Parent / Guardian Consent (P03)",
        help="Parental or legal guardian consent recorded for child-headed household.",
    )

    # [P04] Complaint Record - Reference, Category & Status
    complaint_reference = fields.Char(
        string="Complaint Reference (P04)",
        help="Grievance / complaint tracking ticket reference.",
    )
    complaint_category = fields.Selection(
        selection=[
            ("entitlement", "Entitlement Issue"),
            ("payment", "Payment / Cash-out Issue"),
            ("exclusion", "Targeting / Exclusion Error"),
            ("conduct", "Staff / Partner Conduct"),
            ("other", "Other"),
        ],
        string="Complaint Category (P04)",
        help="Category of beneficiary complaint or grievance.",
    )
    complaint_status = fields.Selection(
        selection=[
            ("received", "Received"),
            ("investigating", "Under Investigation"),
            ("resolved", "Resolved"),
            ("closed", "Closed"),
        ],
        string="Complaint Status (P04)",
        default="received",
        help="Current workflow status of the complaint.",
    )
    complaint_date = fields.Date(
        string="Complaint Date (P04)",
        help="Date when complaint was filed.",
    )
    complaint_notes = fields.Text(
        string="Complaint Notes (P04)",
        help="Summary details of the complaint / grievance.",
    )

    # [P05] Data Correction Requests
    data_correction_ref = fields.Char(
        string="Data Correction Ref (P05)",
        help="Reference number for official data correction / bio-data update request.",
    )
    data_correction_status = fields.Selection(
        selection=[
            ("submitted", "Submitted"),
            ("under_review", "Under Review"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        string="Data Correction Status (P05)",
        default="submitted",
        help="Status of the data correction request.",
    )
    data_correction_date = fields.Date(
        string="Data Correction Date (P05)",
        help="Date when data correction request was submitted.",
    )
    data_correction_notes = fields.Text(
        string="Data Correction Notes (P05)",
        help="Details of requested bio-data corrections.",
    )

    # =========================================================================
    # [CATEGORY Q] Record Status, Closure and Audit (Q01 - Q04)
    # =========================================================================

    # [Q02] Closure Reason and Date - Selection & Date
    closure_reason = fields.Selection(
        selection=[
            ("voluntary_repatriation", "Voluntary Repatriation"),
            ("resettlement", "Resettlement"),
            ("deceased", "Deceased"),
            ("naturalised", "Naturalised"),
            ("duplicate", "Duplicate"),
            ("absent_verification", "Absent at Verification"),
        ],
        string="Closure Reason (Q02)",
        help="Formal reason for household record closure/inactivation.",
    )
    closure_date = fields.Date(
        string="Closure Date (Q02)",
        help="Date when the household record was closed.",
    )

    # [Q03] Duplicate Check - Selection
    duplicate_check = fields.Selection(
        selection=[
            ("unique", "Unique"),
            ("possible_duplicate", "Possible Duplicate"),
            ("confirmed_duplicate", "Confirmed Duplicate"),
            ("merged", "Merged"),
        ],
        string="Duplicate Check Result (Q03)",
        default="unique",
        help="Duplicate detection result (case/manifest or demographic matching).",
    )

    _sql_constraints = [
        (
            "internal_record_id_unique",
            "unique(internal_record_id)",
            "Internal Record ID must be unique per Refugee Group.",
        ),
        (
            "functional_record_id_unique",
            "unique(functional_record_id)",
            "Functional Record ID must be unique per Refugee Group.",
        ),
    ]

    @api.depends("functional_record_id", "household_head_name")
    def _compute_record_name(self):
        for rec in self:
            if rec.household_head_name:
                rec.record_name = f"Group: {rec.household_head_name} ({rec.functional_record_id or rec.internal_record_id or 'New'})"
            else:
                rec.record_name = f"Group ({rec.functional_record_id or rec.internal_record_id or 'New'})"

    @api.depends("head_of_household_id", "head_of_household_id.internal_record_id")
    def _compute_head_internal_id(self):
        for rec in self:
            if rec.head_of_household_id and rec.head_of_household_id.internal_record_id:
                rec.head_of_household_internal_record_id = rec.head_of_household_id.internal_record_id

    @api.depends("head_of_household_id", "head_of_household_id.name")
    def _compute_head_name(self):
        for rec in self:
            if rec.head_of_household_id:
                rec.household_head_name = rec.head_of_household_id.name
            else:
                rec.household_head_name = ""

    @api.depends(
        "member_ids",
        "member_ids.physical_presence_status",
        "member_ids.individual_id.age",
        "member_ids.individual_id.sex",
        "head_of_household_id",
        "head_of_household_id.sex",
        "head_of_household_id.age",
    )
    def _compute_household_composition(self):
        """
        Computes F03 (size), F04 (dependency ratio), F05 (female headed), and F06 (child headed).
        - Household size: Count of present or temporarily absent members. If no member records exist,
          defaults to 1 if head is specified, else 0.
        - Female-headed household: True if head_of_household_id.sex == 'female'.
        - Child-headed household: True if head_of_household_id.age < 18.
        - Dependency ratio: Dependents (age < 15 or >= 65) divided by working-age members (15..64).
        """
        CHILD_AGE_THRESHOLD = 18
        WORKING_AGE_MIN = 15
        WORKING_AGE_MAX = 64

        for rec in self:
            # Active members considered physically present or temporarily absent
            active_members = rec.member_ids.filtered(
                lambda m: m.physical_presence_status in ("present", "temporarily_absent")
            )
            count = len(active_members)
            if count == 0 and rec.head_of_household_id:
                count = 1
            rec.household_size = count

            # [F05] Female headed
            if rec.head_of_household_id and rec.head_of_household_id.sex == "female":
                rec.female_headed_household = True
            else:
                rec.female_headed_household = False

            # [F06] Child headed (< 18)
            if rec.head_of_household_id and rec.head_of_household_id.age > 0 and rec.head_of_household_id.age < CHILD_AGE_THRESHOLD:
                rec.child_headed_household = True
            else:
                rec.child_headed_household = False

            # [F04] Dependency ratio
            # Formula: Number of dependents (<15 or >=65) / Number of working-age members (15-64).
            # Thresholds are proposed and provisional pending formal project-owner approval.
            working_age_count = 0
            dependents_count = 0

            if active_members:
                for member in active_members:
                    ind = member.individual_id
                    age = ind.age if ind else 0
                    if WORKING_AGE_MIN <= age <= WORKING_AGE_MAX:
                        working_age_count += 1
                    else:
                        dependents_count += 1
            elif rec.head_of_household_id:
                head_age = rec.head_of_household_id.age
                if WORKING_AGE_MIN <= head_age <= WORKING_AGE_MAX:
                    working_age_count = 1
                else:
                    dependents_count = 1

            if working_age_count > 0:
                ratio = round(dependents_count / working_age_count, 2)
                rec.dependency_ratio = ratio
                rec.dependency_ratio_display = f"{ratio:.2f}"
                rec.dependency_ratio_status = "calculated"
            elif dependents_count > 0:
                # Safe zero-denominator handling: working-age == 0, dependents > 0
                # Do NOT assign dependent count as dependency ratio.
                rec.dependency_ratio = False
                rec.dependency_ratio_display = "N/A (Zero working-age members in household)"
                rec.dependency_ratio_status = "zero_working_age"
            else:
                # Zero working-age and zero dependents (no active members)
                rec.dependency_ratio = False
                rec.dependency_ratio_display = "N/A (No active members in household)"
                rec.dependency_ratio_status = "no_members"

    @api.constrains("latitude", "longitude")
    def _check_gps_coordinates(self):
        """
        [G07] Validates that dwelling GPS latitude and longitude are valid decimal coordinates.
        - Latitude range: -90.0 to +90.0 degrees (Uganda approx: -1.5 to +4.5).
        - Longitude range: -180.0 to +180.0 degrees (Uganda approx: +29.5 to +35.0).
        """
        for rec in self:
            if rec.latitude:
                try:
                    lat = float(rec.latitude)
                    if not (-90.0 <= lat <= 90.0):
                        raise ValidationError(
                            f"Invalid Latitude '{rec.latitude}'. Latitude must be between -90.0 and +90.0 degrees."
                        )
                except ValueError:
                    raise ValidationError(
                        f"Invalid Latitude format '{rec.latitude}'. Must be a valid decimal number."
                    )
            if rec.longitude:
                try:
                    lon = float(rec.longitude)
                    if not (-180.0 <= lon <= 180.0):
                        raise ValidationError(
                            f"Invalid Longitude '{rec.longitude}'. Longitude must be between -180.0 and +180.0 degrees."
                        )
                except ValueError:
                    raise ValidationError(
                        f"Invalid Longitude format '{rec.longitude}'. Must be a valid decimal number."
                    )

    @api.depends("income_sources")
    def _compute_income_sources_display(self):
        for rec in self:
            if isinstance(rec.income_sources, list):
                rec.income_sources_display = ", ".join(str(s).replace("_", " ").title() for s in rec.income_sources)
            elif rec.income_sources:
                rec.income_sources_display = str(rec.income_sources)
            else:
                rec.income_sources_display = ""

    @api.depends("productive_assets")
    def _compute_productive_assets_display(self):
        for rec in self:
            if isinstance(rec.productive_assets, list):
                rec.productive_assets_display = ", ".join(str(s).replace("_", " ").title() for s in rec.productive_assets)
            elif rec.productive_assets:
                rec.productive_assets_display = str(rec.productive_assets)
            else:
                rec.productive_assets_display = ""

    @api.constrains("income_sources")
    def _check_income_sources(self):
        for rec in self:
            if isinstance(rec.income_sources, list) and "none" in rec.income_sources and len(rec.income_sources) > 1:
                raise ValidationError("Income source 'None' cannot be combined with other income sources (L01).")

    @api.constrains("productive_assets")
    def _check_productive_assets(self):
        for rec in self:
            if isinstance(rec.productive_assets, list) and "none" in rec.productive_assets and len(rec.productive_assets) > 1:
                raise ValidationError("Productive asset 'None' cannot be combined with other productive assets (L04).")

    @api.constrains("working_age_earners_count", "member_ids", "member_ids.individual_id.age", "head_of_household_id.age")
    def _check_working_age_earners(self):
        for rec in self:
            if rec.working_age_earners_count < 0:
                raise ValidationError("Working-age earners count cannot be negative (L02).")
            # Calculate working-age count (15-64)
            active_members = rec.member_ids.filtered(lambda m: m.physical_presence_status in ("present", "temporarily_absent"))
            if active_members:
                working_age_count = sum(1 for m in active_members if m.individual_id and 15 <= m.individual_id.age <= 64)
            else:
                working_age_count = 1 if (rec.head_of_household_id and 15 <= rec.head_of_household_id.age <= 64) else 0
            if rec.working_age_earners_count > working_age_count:
                raise ValidationError(
                    f"Number of working-age members earning income ({rec.working_age_earners_count}) cannot exceed the count of working-age members ({working_age_count}) in the household (L02)."
                )

    @api.constrains("monthly_household_income")
    def _check_monthly_income(self):
        for rec in self:
            if rec.monthly_household_income is not False and rec.monthly_household_income is not None and rec.monthly_household_income < 0:
                raise ValidationError("Monthly household income cannot be negative (L08).")

    @api.constrains("vulnerability_score")
    def _check_group_vulnerability_score(self):
        for rec in self:
            if rec.vulnerability_score is not False and rec.vulnerability_score is not None:
                if not (0.0 <= rec.vulnerability_score <= 100.0):
                    raise ValidationError(
                        f"Vulnerability score must be between 0.0 and 100.0 (received: {rec.vulnerability_score})."
                    )

    @api.depends("account_number")
    def _compute_account_number_masked(self):
        for rec in self:
            acc = rec.sudo().account_number
            if acc and len(acc) > 4:
                rec.account_number_masked = "*" * (len(acc) - 4) + acc[-4:]
            elif acc:
                rec.account_number_masked = "****"
            else:
                rec.account_number_masked = ""

    @api.depends("consent_information_sharing", "informed_consent")
    def _compute_consent_sharing_display(self):
        for rec in self:
            if rec.informed_consent in ("no", "withdrawn"):
                rec.consent_sharing_display = "WITHDRAWN - Sharing Prohibited"
            elif isinstance(rec.consent_information_sharing, list) and rec.consent_information_sharing:
                rec.consent_sharing_display = ", ".join(str(s).upper() for s in rec.consent_information_sharing)
            elif rec.consent_information_sharing:
                rec.consent_sharing_display = str(rec.consent_information_sharing)
            else:
                rec.consent_sharing_display = "None"

    def write(self, vals):
        if vals.get("informed_consent") in ("no", "withdrawn") and "consent_information_sharing" not in vals:
            vals["consent_information_sharing"] = []
        return super().write(vals)

    @api.constrains("enrolment_date", "exit_date", "exit_reason")
    def _check_enrolment_exit_dates(self):
        """
        [M05] Validates consistency of enrolment date, exit date, and required exit reason.
        """
        for rec in self:
            if rec.enrolment_date and rec.exit_date and rec.exit_date < rec.enrolment_date:
                raise ValidationError("Programme exit date cannot be earlier than the programme enrolment date (M05).")
            if rec.exit_date and not rec.exit_reason:
                raise ValidationError("An exit reason must be specified when recording a programme exit date (M05).")
            if rec.exit_reason and not rec.exit_date:
                raise ValidationError("Programme exit date must be specified when recording an exit reason (M05).")

    @api.constrains("record_status", "closure_reason", "closure_date")
    def _check_record_closure(self):
        """
        [Q01, Q02] Validates that closing a household record requires closure reason and date.
        """
        for rec in self:
            if rec.record_status == "closed":
                if not rec.closure_reason:
                    raise ValidationError("Closure reason must be provided when record status is set to Closed (Q02).")
                if not rec.closure_date:
                    raise ValidationError("Closure date must be provided when record status is set to Closed (Q02).")
            elif (rec.closure_reason or rec.closure_date) and rec.record_status != "closed":
                raise ValidationError("Closure reason and date are only applicable when record status is Closed (Q02).")

    @api.constrains("primary_recipient_id", "alternate_recipient_id")
    def _check_payment_recipients(self):
        """
        [N06, N07] Validates that alternate recipient is distinct from primary recipient.
        """
        for rec in self:
            if rec.primary_recipient_id and rec.alternate_recipient_id and rec.primary_recipient_id.id == rec.alternate_recipient_id.id:
                raise ValidationError("Alternate recipient / proxy cannot be the same individual as the primary recipient (N07).")

    @api.constrains("informed_consent", "consent_date", "consent_information_sharing")
    def _check_informed_consent(self):
        """
        [P01, P02] Validates that informed consent date is recorded when consent is granted,
        and ensures data sharing is prohibited when consent is withdrawn.
        """
        for rec in self:
            if rec.informed_consent == "yes" and not rec.consent_date:
                raise ValidationError("Consent date must be recorded when informed consent is granted (P01).")
            if rec.informed_consent in ("no", "withdrawn") and rec.consent_information_sharing:
                raise ValidationError(
                    "Data sharing permissions cannot be active when informed consent is withdrawn or not granted (P01/P02)."
                )

    @api.constrains("entitlement_amount")
    def _check_entitlement_amount(self):
        """
        [N09] Validates that entitlement amount is non-negative.
        """
        for rec in self:
            if rec.entitlement_amount < 0.0:
                raise ValidationError("Entitlement amount must be a non-negative amount in UGX (N09).")

    @api.constrains("payment_cycle")
    def _check_payment_cycle_format(self):
        """
        [O01] Validates that payment cycle matches YYYY-MM format.
        """
        import re
        for rec in self:
            if rec.payment_cycle and not re.match(r"^\d{4}-(0[1-9]|1[0-2])$", rec.payment_cycle):
                raise ValidationError(
                    f"Payment cycle '{rec.payment_cycle}' must follow the standard YYYY-MM format (e.g. 2024-11) (O01)."
                )


class G2PRefugeeGroupMember(models.Model):
    _name = "g2p.refugee.group.member"
    _description = "Refugee Group Member Association"
    _rec_name = "individual_id"

    group_id = fields.Many2one(
        "g2p.register.refugee_group",
        string="Refugee Group",
        required=True,
        ondelete="cascade",
        index=True,
    )
    individual_id = fields.Many2one(
        "g2p.register.refugee_individual",
        string="Refugee Individual",
        required=True,
        index=True,
    )

    # Member details mirrored for convenience
    surname = fields.Char(related="individual_id.surname", readonly=True)
    given_names = fields.Char(related="individual_id.given_names", readonly=True)
    sex = fields.Selection(related="individual_id.sex", readonly=True)
    date_of_birth = fields.Date(related="individual_id.date_of_birth", readonly=True)
    age = fields.Integer(related="individual_id.age", readonly=True)

    # [F02] Relationship to Head - Selection (per member)
    relationship_to_head = fields.Selection(
        selection=[
            ("self", "Self / Head"),
            ("spouse", "Spouse"),
            ("child", "Child (Son / Daughter)"),
            ("parent", "Parent (Father / Mother)"),
            ("sibling", "Sibling (Brother / Sister)"),
            ("grandparent", "Grandparent"),
            ("grandchild", "Grandchild"),
            ("other_relative", "Other Relative"),
            ("non_relative", "Non-Relative"),
        ],
        string="Relationship to Head (F02)",
        required=True,
        default="child",
    )

    # [F07] Members Not Physically Present / Presence Status - Selection (per member)
    physical_presence_status = fields.Selection(
        selection=[
            ("present", "Present"),
            ("temporarily_absent", "Temporarily Absent"),
            ("left", "Left"),
            ("deceased", "Deceased"),
        ],
        string="Physical Presence Status (F07)",
        required=True,
        default="present",
    )

    _sql_constraints = [
        (
            "group_individual_unique",
            "unique(group_id, individual_id)",
            "An individual refugee can only be added once to the same refugee group.",
        )
    ]
