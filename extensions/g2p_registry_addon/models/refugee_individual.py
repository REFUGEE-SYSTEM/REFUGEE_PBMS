from odoo import models, fields, api
from odoo.exceptions import ValidationError

from .registry import G2PRegistry


class G2PRefugeeSpecificNeed(models.Model):
    _name = "g2p.refugee.specific_need"
    _description = "Refugee Specific Need Category (Configurable)"
    _rec_name = "name"
    """
    Standard UNHCR Specific Needs Codes Taxonomy (ProGres v4).
    Standard codes include:
    - CR: Child at risk
    - WR: Woman at risk
    - ER: Older person at risk
    - DS: Disability
    - SM: Serious medical condition
    - LP: Legal and physical protection needs
    Marked as provisional standard configuration pending formal OPM/UNHCR localized mapping approval.
    """

    code = fields.Char(string="Code", required=True, index=True)
    name = fields.Char(string="Category Name", required=True)
    description = fields.Text(string="Description")
    active = fields.Boolean(string="Active", default=True)

    _sql_constraints = [
        ("code_uniq", "unique(code)", "Specific Need Code must be unique!"),
    ]


class G2PRefugeeIndividualRegistry(models.Model):
    _name = "g2p.register.refugee_individual"
    _description = "Refugee Individual Registry"
    _inherit = "g2p.registry"
    _rec_name = "functional_record_id"

    # Base Registry Fields
    functional_record_id = fields.Char(string="Functional Record ID", index=True)
    link_internal_record_id = fields.Char(string="Link Internal Record ID", index=True)
    link_foundational_id = fields.Char(string="Link Foundational ID", index=True)
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
    # [CATEGORY A] Registration & Movement Attributes
    # =========================================================================

    # [A02] Registration Date - Date
    registration_date = fields.Date(
        string="Registration Date (A02)",
        help="Date when the individual refugee record was registered.",
    )

    # [A03] Arrival Date in Uganda - Date
    arrival_date = fields.Date(
        string="Arrival Date in Uganda (A03)",
        help="Date of physical arrival into the host country (Uganda).",
    )

    # =========================================================================
    # [CATEGORY B] Personal Identity Attributes
    # =========================================================================

    # [B01] Surname / Family Name - Text, Uppercase
    surname = fields.Char(string="Surname / Family Name (B01)", required=True, index=True)

    # [B02] Given Name(s) - Text, Free text
    given_names = fields.Char(string="Given Name(s) (B02)", required=True)

    # [B03] Other / Additional Names - Text, Free text
    other_names = fields.Char(
        string="Other / Additional Names (B03)",
        help="Aliases, nicknames, maiden name, or other names by which the individual is known.",
    )

    # Display / Full Name (Helper)
    name = fields.Char(string="Full Name", compute="_compute_name", store=True)

    # [B04] Sex - Selection: Male, Female
    sex = fields.Selection(
        selection=[
            ("male", "Male"),
            ("female", "Female"),
        ],
        string="Sex (B04)",
        required=True,
    )

    # [B05] Date of Birth - Date: DD/MM/YYYY
    date_of_birth = fields.Date(string="Date of Birth (B05)", required=True)

    # [B06] Date of Birth is Estimated? - Boolean: Yes / No
    date_of_birth_estimated = fields.Boolean(
        string="Date of Birth is Estimated? (B06)",
        default=False,
    )

    # [B07] Place of Birth - Text: Place and country code
    place_of_birth = fields.Char(string="Place of Birth (B07)")

    # [B08] Country of Origin - Selection: ISO 3166 country list
    country_of_origin = fields.Selection(
        selection=[
            ("AFG", "Afghanistan"),
            ("BDI", "Burundi"),
            ("COD", "Congo, Democratic Republic of the"),
            ("ERI", "Eritrea"),
            ("ETH", "Ethiopia"),
            ("IRQ", "Iraq"),
            ("MMR", "Myanmar"),
            ("PSE", "Palestine, State of"),
            ("RWA", "Rwanda"),
            ("SOM", "Somalia"),
            ("SSD", "South Sudan"),
            ("SDN", "Sudan"),
            ("SYR", "Syrian Arab Republic"),
            ("UKR", "Ukraine"),
            ("VEN", "Venezuela, Bolivarian Republic of"),
            ("YEM", "Yemen"),
            ("OTHER", "Other Country"),
        ],
        string="Country of Origin (B08)",
        required=True,
    )
    country_of_origin_code = fields.Char(string="Country of Origin Code (ISO 3166)")

    # [B09] Nationality / Citizenship - Selection: ISO country list, Stateless, Undetermined
    nationality = fields.Selection(
        selection=[
            ("AFG", "Afghanistan"),
            ("BDI", "Burundi"),
            ("COD", "Congo, Democratic Republic of the"),
            ("ERI", "Eritrea"),
            ("ETH", "Ethiopia"),
            ("IRQ", "Iraq"),
            ("MMR", "Myanmar"),
            ("PSE", "Palestine, State of"),
            ("RWA", "Rwanda"),
            ("SOM", "Somalia"),
            ("SSD", "South Sudan"),
            ("SDN", "Sudan"),
            ("SYR", "Syrian Arab Republic"),
            ("UKR", "Ukraine"),
            ("VEN", "Venezuela, Bolivarian Republic of"),
            ("YEM", "Yemen"),
            ("STATELESS", "Stateless"),
            ("UNDETERMINED", "Undetermined"),
            ("OTHER", "Other Nationality"),
        ],
        string="Nationality / Citizenship (B09)",
        required=True,
    )

    # [B10] Marital Status - Selection: Single, Married, Divorced, Separated, Widowed, Engaged
    marital_status = fields.Selection(
        selection=[
            ("single", "Single"),
            ("married", "Married"),
            ("divorced", "Divorced"),
            ("separated", "Separated"),
            ("widowed", "Widowed"),
            ("engaged", "Engaged"),
        ],
        string="Marital Status (B10)",
    )

    # [B11] Preferred Language(s) - Multi-selection
    preferred_languages = fields.Json(
        string="Preferred Language(s) (B11)",
        default=list,
    )
    preferred_languages_display = fields.Char(
        string="Preferred Languages Display",
        compute="_compute_preferred_languages_display",
        store=True,
    )

    # [B12] Literacy - Selection (Yes / No)
    literacy_status = fields.Selection(
        selection=[
            ("yes", "Yes"),
            ("no", "No"),
        ],
        string="Literacy (B12)",
        help="Indicates whether the individual is literate (Yes / No) according to the data dictionary.",
    )

    # [B13] Ethnicity / Tribe - Text (Special Category Data)
    ethnicity_tribe = fields.Char(
        string="Ethnicity / Tribe (B13)",
        groups="g2p_pbms.group_program_super_administration,base.group_erp_manager",
        help="Ethnic group, clan, or tribe affiliation. Special category sensitive data.",
    )

    # [B14] Religion - Selection (Special Category Data)
    religion = fields.Selection(
        selection=[
            ("christianity", "Christianity"),
            ("islam", "Islam"),
            ("traditional", "Traditional / Indigenous Beliefs"),
            ("other", "Other"),
            ("none", "No Religion"),
            ("prefer_not_to_say", "Prefer not to say"),
        ],
        string="Religion (B14)",
        groups="g2p_pbms.group_program_super_administration,base.group_erp_manager",
        help="Religious affiliation. Special category sensitive data.",
    )

    # Computed age in years
    age = fields.Integer(string="Age", compute="_compute_age", store=True)

    # =========================================================================
    # [CATEGORY C] Biometrics Attributes
    # =========================================================================

    # [C01] Facial Photograph - Binary/Image (Attachment)
    photo = fields.Binary(
        string="Facial Photograph (C01)",
        attachment=True,
        help="High-resolution facial image conforming to ICAO biometric standards.",
    )

    # [C02] Fingerprints - Capture Status & Secure Token Reference
    biometric_fingerprint_status = fields.Selection(
        selection=[
            ("not_captured", "Not Captured"),
            ("captured", "Captured"),
            ("exempt", "Exempt"),
            ("failed", "Failed Capture"),
        ],
        string="Fingerprint Status (C02)",
        default="not_captured",
        help="Biometric fingerprint enrolment status.",
    )
    fingerprint_token_ref = fields.Char(
        string="Fingerprint Template Ref / Token (C02)",
        help="Reference token to the biometric server or secure credential store. Never store raw templates in plaintext.",
    )

    # [C03] Iris Scan - Capture Status & Secure Token Reference
    biometric_iris_status = fields.Selection(
        selection=[
            ("not_captured", "Not Captured"),
            ("captured", "Captured"),
            ("exempt", "Exempt"),
            ("failed", "Failed Capture"),
        ],
        string="Iris Scan Status (C03)",
        default="not_captured",
        help="Biometric iris scan enrolment status.",
    )
    iris_token_ref = fields.Char(
        string="Iris Template Ref / Token (C03)",
        help="Reference token to the iris matching service or credential store.",
    )

    # [C04] Biometric Exemption Reason - Selection
    biometric_exemption_reason = fields.Selection(
        selection=[
            ("under_age", "Under age"),
            ("disability", "Disability"),
            ("injury", "Injury"),
            ("equipment_failure", "Equipment failure"),
            ("other", "Other"),
        ],
        string="Biometric Exemption Reason (C04)",
        help="Official justification recorded when biometric capture is exempted: Under age, Disability, Injury, Equipment failure, Other.",
    )

    # [C05] Last Biometric Verification Date - Datetime
    last_biometric_verification_date = fields.Datetime(
        string="Last Biometric Verification Date (C05)",
        help="Timestamp of the most recent successful biometric authentication.",
    )

    # =========================================================================
    # [CATEGORY D] Identity Documents Attributes
    # =========================================================================

    # [D01] Identity Document Type & Registration Number
    document_type = fields.Selection(
        selection=[
            ("unhcr_individual_id", "UNHCR Individual Registration Number"),
            ("opm_attestation", "OPM Attestation / Family Card"),
            ("refugee_id_card", "Government Refugee Identity Card"),
            ("asylum_seeker_cert", "Asylum Seeker Certificate"),
            ("convention_travel_doc", "Convention Travel Document (CTD)"),
            ("birth_notification", "Birth Notification / Certificate"),
            ("other", "Other Official Document"),
        ],
        string="Identity Document Type (D01)",
        default="unhcr_individual_id",
        help="Primary legal or administrative document held by the refugee individual.",
    )
    document_number = fields.Char(
        string="Refugee / Document Registration Number (D01)",
        index=True,
        help="Official registration or serial number of the identity document.",
    )
    document_issue_date = fields.Date(
        string="Document Issue Date (D01)",
        help="Date the identity document was issued.",
    )
    document_expiry_date = fields.Date(
        string="Document Expiry Date (D01)",
        help="Expiration date of the identity document, if applicable.",
    )

    # =========================================================================
    # [CATEGORY E] Legal Status & RSD Attributes
    # =========================================================================

    # [E01] Legal Status - Selection (PROVISIONAL - Pending External Refugee Registry Code List)
    # Statutory Source Mapping:
    # 1. 'refugee_prima_facie': Recognized Refugee (Prima Facie) - Uganda Refugees Act 2006, Section 25.
    # 2. 'refugee_individual_rsd': Recognized Refugee (Individual RSD) - Uganda Refugees Act 2006, Section 4 & 21.
    # 3. 'asylum_seeker': Asylum Seeker - Uganda Refugees Act 2006, Section 19.
    # 4. 'rejected_asylum_seeker': Rejected Asylum Seeker - Uganda Refugees Act 2006, Section 22 & 23.
    # 5. 'stateless': Stateless Person - 1954 Convention / EAC regional guidelines.
    # 6. 'complementary_protection': Temporary / Complementary Protection - OPM humanitarian declaration.
    # 7. 'other': Other Legal Status.
    legal_status = fields.Selection(
        selection=[
            ("refugee_prima_facie", "Recognized Refugee (Prima Facie)"),
            ("refugee_individual_rsd", "Recognized Refugee (Individual RSD)"),
            ("asylum_seeker", "Asylum Seeker"),
            ("rejected_asylum_seeker", "Rejected Asylum Seeker"),
            ("stateless", "Stateless Person"),
            ("complementary_protection", "Temporary / Complementary Protection"),
            ("other", "Other Legal Status"),
        ],
        string="Legal Status (E01) [Provisional]",
        default="refugee_prima_facie",
        help="Provisional legal status code list based on Uganda Refugees Act 2006 and UNHCR/OPM SOPs. Pending final API code list specification.",
    )

    # [E03] RSD Application Date - Date
    rsd_application_date = fields.Date(
        string="RSD Application Date (E03)",
        help="Date of formal application for Refugee Status Determination.",
    )

    # [E04] RSD Interview Date - Date
    rsd_interview_date = fields.Date(
        string="RSD Interview Date (E04)",
        help="Date of first-instance RSD substantive interview.",
    )

    # [E05] REC Decision & Date - Selection (Granted, Rejected, Pending) & Date
    rec_decision = fields.Selection(
        selection=[
            ("granted", "Granted"),
            ("rejected", "Rejected"),
            ("pending", "Pending"),
        ],
        string="REC Decision (E05)",
        help="Refugee Eligibility Committee first-instance decision (Granted, Rejected, Pending).",
    )
    rec_decision_date = fields.Date(
        string="REC Decision Date (E05)",
        help="Date of REC decision notification.",
    )

    # [E06] Appeal Stage & Outcome - Selection (None, REC review, RAB appeal, Upheld, Overturned) & Date
    rsd_appeal_stage = fields.Selection(
        selection=[
            ("none", "None"),
            ("rec_review", "REC review"),
            ("rab_appeal", "RAB appeal"),
            ("upheld", "Upheld"),
            ("overturned", "Overturned"),
        ],
        string="Appeal Stage & Outcome (E06)",
        default="none",
        help="Stage and outcome of appeal (None, REC review, RAB appeal, Upheld, Overturned).",
    )
    rsd_appeal_date = fields.Date(
        string="RSD Appeal Date (E06)",
        help="Date of appeal submission or decision.",
    )

    # [E07] Security Screening Cleared? - Selection (Cleared, Pending, Referred) & Date
    security_screening_status = fields.Selection(
        selection=[
            ("cleared", "Cleared"),
            ("pending", "Pending"),
            ("referred", "Referred"),
        ],
        string="Security Screening Status (E07)",
        default="pending",
        help="Government/authorized security vetting status (Cleared, Pending, Referred).",
    )
    security_screening_cleared = fields.Boolean(
        string="Security Screening Cleared? (E07)",
        compute="_compute_security_screening_cleared",
        store=True,
        help="True if security vetting status is Cleared.",
    )
    security_screening_date = fields.Date(
        string="Security Screening Date (E07)",
        help="Date when security vetting was completed.",
    )

    # [E08] Independent Registration at 18 - Boolean & Date
    independent_registration_at_18 = fields.Boolean(
        string="Independent Registration at 18 (E08)",
        default=False,
        help="Flagged when an individual originally registered under a parent/guardian file turns 18 and obtains an independent registration record.",
    )
    independent_registration_date = fields.Date(
        string="Independent Registration Date (E08)",
        help="Date when the individual obtained independent registration upon turning 18.",
    )

    # =========================================================================
    # [CATEGORY I] Specific Needs & Protection Attributes
    # =========================================================================

    # [I01] Specific Needs Category - Many2many to configurable categories
    specific_need_ids = fields.Many2many(
        "g2p.refugee.specific_need",
        "g2p_refugee_ind_specific_need_rel",
        "individual_id",
        "need_id",
        string="Specific Needs Categories (I01)",
        groups="g2p_pbms.group_program_super_administration,base.group_erp_manager",
        help="Specific needs categories. Configurable relational model pending official UNHCR/OPM code list integration.",
    )

    # [I02] Unaccompanied / Separated Child - Selection (Unassessed, Unaccompanied, Separated, Accompanied, Not Applicable)
    uasc_status = fields.Selection(
        selection=[
            ("unassessed", "Not Assessed / Unknown"),
            ("unaccompanied", "Unaccompanied Child"),
            ("separated", "Separated Child"),
            ("accompanied", "Accompanied Child"),
            ("not_applicable", "Not Applicable (Adult)"),
        ],
        string="Unaccompanied / Separated Child (I02)",
        default="unassessed",
        groups="g2p_pbms.group_program_super_administration,base.group_erp_manager",
        help="Indicates whether a minor is an unaccompanied child, separated child, accompanied, or not applicable. Defaults to unassessed to avoid misclassification.",
    )

    # [I03] Caregiver Reference - Many2one to Refugee Individual
    caregiver_individual_id = fields.Many2one(
        "g2p.register.refugee_individual",
        string="Caregiver Reference (I03)",
        groups="g2p_pbms.group_program_super_administration,base.group_erp_manager",
        help="Reference to another registered refugee individual who serves as primary caregiver for the child.",
    )
    caregiver_relationship = fields.Char(
        string="Caregiver Relationship (I03)",
        groups="g2p_pbms.group_program_super_administration,base.group_erp_manager",
        help="Nature of relationship between the child and caregiver (e.g. aunt, uncle, foster parent, unrelated adult).",
    )

    # [I04] Protection Referral - Yes/No and Referral Date
    has_protection_referral = fields.Selection(
        selection=[
            ("yes", "Yes"),
            ("no", "No"),
        ],
        string="Protection Referral Exists? (I04)",
        default="no",
        groups="g2p_pbms.group_program_super_administration,base.group_erp_manager",
        help="Indicates whether a formal protection referral has been initiated.",
    )
    protection_referral_date = fields.Date(
        string="Protection Referral Date (I04)",
        groups="g2p_pbms.group_program_super_administration,base.group_erp_manager",
        help="Date when the protection referral was recorded.",
    )

    # =========================================================================
    # [CATEGORY J] Health, Disability & Nutrition Attributes
    # =========================================================================

    # [J01] Washington Group Short Set on Disability - 6 Separate Domains
    WG_SELECTION = [
        ("no_difficulty", "No difficulty"),
        ("some_difficulty", "Some difficulty"),
        ("lot_of_difficulty", "A lot of difficulty"),
        ("cannot_do", "Cannot do at all"),
    ]

    wg_seeing = fields.Selection(
        selection=WG_SELECTION,
        string="WG: Seeing (J01)",
        groups="g2p_pbms.group_program_super_administration,base.group_erp_manager",
        help="Do you have difficulty seeing, even if wearing glasses?",
    )
    wg_hearing = fields.Selection(
        selection=WG_SELECTION,
        string="WG: Hearing (J01)",
        groups="g2p_pbms.group_program_super_administration,base.group_erp_manager",
        help="Do you have difficulty hearing, even if using a hearing aid?",
    )
    wg_walking = fields.Selection(
        selection=WG_SELECTION,
        string="WG: Walking (J01)",
        groups="g2p_pbms.group_program_super_administration,base.group_erp_manager",
        help="Do you have difficulty walking or climbing steps?",
    )
    wg_remembering = fields.Selection(
        selection=WG_SELECTION,
        string="WG: Remembering (J01)",
        groups="g2p_pbms.group_program_super_administration,base.group_erp_manager",
        help="Do you have difficulty remembering or concentrating?",
    )
    wg_selfcare = fields.Selection(
        selection=WG_SELECTION,
        string="WG: Self-care (J01)",
        groups="g2p_pbms.group_program_super_administration,base.group_erp_manager",
        help="Do you have difficulty with self-care, such as washing all over or dressing?",
    )
    wg_communicating = fields.Selection(
        selection=WG_SELECTION,
        string="WG: Communicating (J01)",
        groups="g2p_pbms.group_program_super_administration,base.group_erp_manager",
        help="Using your usual language, do you have difficulty communicating, for example understanding or being understood?",
    )

    # [J02] Serious Medical Condition / Chronic Illness - Yes/No & Notes
    has_serious_medical_condition = fields.Selection(
        selection=[
            ("yes", "Yes"),
            ("no", "No"),
        ],
        string="Serious Medical / Chronic Illness (J02)",
        groups="g2p_pbms.group_program_super_administration,base.group_erp_manager",
        help="Presence of a serious medical condition or chronic illness.",
    )
    serious_medical_condition_notes = fields.Char(
        string="Medical Condition Notes (J02)",
        groups="g2p_pbms.group_program_super_administration,base.group_erp_manager",
        help="Supplementary non-clinical notes regarding serious medical condition.",
    )

    # [J03] Pregnancy / Lactation Status - Selection (Pregnant, Lactating, No)
    pregnant_lactating_status = fields.Selection(
        selection=[
            ("pregnant", "Pregnant"),
            ("lactating", "Lactating"),
            ("no", "No"),
        ],
        string="Pregnancy / Lactation Status (J03)",
        default="no",
        groups="g2p_pbms.group_program_super_administration,base.group_erp_manager",
        help="Current pregnancy or lactation status.",
    )

    # [J04] Child Under 5 MUAC / Nutrition Status - MUAC Score & Nutrition Category
    muac_score = fields.Float(
        string="MUAC Score in mm (J04)",
        digits=(5, 1),
        groups="g2p_pbms.group_program_super_administration,base.group_erp_manager",
        help="Mid-Upper Arm Circumference measurement in millimetres (for children aged 6 to 59 months).",
    )
    nutrition_status = fields.Selection(
        selection=[
            ("normal", "Normal"),
            ("mam", "MAM"),
            ("sam", "SAM"),
        ],
        string="Nutrition Status (J04)",
        groups="g2p_pbms.group_program_super_administration,base.group_erp_manager",
        help="Nutrition assessment category: Normal, MAM (Moderate Acute Malnutrition), SAM (Severe Acute Malnutrition).",
    )

    # [J05] Vaccination Status - Yes/No
    vaccination_status = fields.Selection(
        selection=[
            ("yes", "Yes"),
            ("no", "No"),
        ],
        string="Vaccination Status (J05)",
        groups="g2p_pbms.group_program_super_administration,base.group_erp_manager",
        help="Indicates whether routine childhood / entry vaccinations are recorded as received (Yes / No).",
    )

    # =========================================================================
    # [CATEGORY K] Education & Skills Attributes (K01 - K03)
    # =========================================================================

    # [K01] Highest Education Level - Selection
    education_level = fields.Selection(
        selection=[
            ("none", "None"),
            ("primary", "Primary"),
            ("secondary", "Secondary"),
            ("vocational", "Vocational"),
            ("tertiary", "Tertiary"),
        ],
        string="Highest Education Level (K01)",
        help="Highest level of formal education completed according to approved data dictionary categories.",
    )

    # [K02] School Enrolment - Selection (children 6–17)
    school_enrolment = fields.Selection(
        selection=[
            ("enrolled", "Enrolled"),
            ("not_enrolled", "Not enrolled"),
            ("dropped_out", "Dropped out"),
        ],
        string="School Enrolment (K02)",
        help="Current school enrolment status for school-age individuals (children 6–17).",
    )

    # [K03] Occupation / Skills - Multi-select
    occupation_skills = fields.Json(
        string="Occupation / Skills (K03)",
        default=list,
        help="Occupations and technical skills: Farming, Trade, Construction, Tailoring, Teaching, Health, Other.",
    )
    occupation_skills_display = fields.Char(
        string="Occupation / Skills Display",
        compute="_compute_occupation_skills_display",
        store=True,
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
        help="Indicates whether the refugee individual is classified as a new arrival.",
    )
    new_arrival_end_date = fields.Date(
        string="New-Arrival End Date (M03)",
        help="Expiry date for new-arrival status / transitional assistance.",
    )

    # [M04] Programmes Enrolled - PBMS Native Programme Membership
    enrolled_program_ids = fields.Many2many(
        "g2p.program.definition",
        "g2p_refugee_ind_program_rel",
        "individual_id",
        "program_id",
        string="Enrolled Programmes (M04)",
        help="Active PBMS social protection programmes in which the refugee is enrolled.",
    )

    # [M05] Enrolment / Exit Date and Reason
    enrolment_date = fields.Date(
        string="Programme Enrolment Date (M05)",
        help="Date when the individual was enrolled in PBMS assistance.",
    )
    exit_date = fields.Date(
        string="Programme Exit Date (M05)",
        help="Date when the individual exited the programme.",
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
        help="Assistance delivery mechanism modality.",
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
        help="FSP contracted or designated for assistance disbursement (e.g. MTN Uganda, Airtel Money, PostBank, Centenary Bank).",
    )

    # [N04] Account / Mobile Money Number - Protected Text
    account_number = fields.Char(
        string="Account / Mobile Money Number (N04)",
        groups="g2p_pbms.group_program_super_administration,base.group_erp_manager",
        help="Bank account or mobile money telephone number for payment delivery. Highly protected financial data.",
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
        help="Indicates whether beneficiary identity matches FSP KYC customer records.",
    )

    # [N06] Primary Recipient - Reference to Individual Refugee
    primary_recipient_id = fields.Many2one(
        "g2p.register.refugee_individual",
        string="Primary Recipient (N06)",
        help="Designated primary payment recipient.",
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
        help="Approved individual entitlement disbursement amount in Uganda Shillings (UGX).",
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
        help="Indicates whether this record is sampled for post-distribution monitoring evaluation.",
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
        help="Informed consent obtained from the beneficiary for registration and assistance.",
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
        help="Parental or legal guardian consent recorded for a child.",
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
        help="Formal reason for record closure/inactivation.",
    )
    closure_date = fields.Date(
        string="Closure Date (Q02)",
        help="Date when the record was closed.",
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
        help="Duplicate detection result (biometric or demographic matching).",
    )

    _sql_constraints = [
        (
            "internal_record_id_unique",
            "unique(internal_record_id)",
            "Internal Record ID must be unique per Refugee Individual.",
        ),
        (
            "functional_record_id_unique",
            "unique(functional_record_id)",
            "Functional Record ID must be unique per Refugee Individual.",
        ),
    ]

    @api.depends("surname", "given_names")
    def _compute_name(self):
        for rec in self:
            parts = [p for p in [rec.given_names, rec.surname] if p]
            rec.name = " ".join(parts) if parts else rec.functional_record_id or rec.internal_record_id

    @api.depends("date_of_birth")
    def _compute_age(self):
        today = fields.Date.today()
        for rec in self:
            if rec.date_of_birth:
                dob = rec.date_of_birth
                years = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                rec.age = max(years, 0)
            else:
                rec.age = 0

    @api.depends("preferred_languages")
    def _compute_preferred_languages_display(self):
        for rec in self:
            if isinstance(rec.preferred_languages, list):
                rec.preferred_languages_display = ", ".join(str(l) for l in rec.preferred_languages)
            elif rec.preferred_languages:
                rec.preferred_languages_display = str(rec.preferred_languages)
            else:
                rec.preferred_languages_display = ""

    @api.depends("occupation_skills")
    def _compute_occupation_skills_display(self):
        for rec in self:
            if isinstance(rec.occupation_skills, list):
                rec.occupation_skills_display = ", ".join(str(s).title() for s in rec.occupation_skills)
            elif rec.occupation_skills:
                rec.occupation_skills_display = str(rec.occupation_skills)
            else:
                rec.occupation_skills_display = ""

    @api.depends("security_screening_status")
    def _compute_security_screening_cleared(self):
        for rec in self:
            rec.security_screening_cleared = (rec.security_screening_status == "cleared")

    @api.onchange("surname")
    def _onchange_surname(self):
        if self.surname:
            self.surname = self.surname.upper()

    @api.constrains("surname")
    def _check_surname(self):
        for rec in self:
            if rec.surname and not rec.surname.isupper():
                rec.surname = rec.surname.upper()

    @api.constrains("muac_score", "nutrition_status", "date_of_birth", "age")
    def _check_nutrition_under_five(self):
        """
        [J04] Validates that child MUAC measurement and under-5 nutrition status
        are only recorded for children under five years of age (age < 5) and
        measurement is a positive value.
        """
        for rec in self:
            if rec.muac_score < 0:
                raise ValidationError("MUAC score must be a positive measurement in millimetres (J04).")
            if (rec.muac_score > 0 or rec.nutrition_status) and rec.age >= 5:
                raise ValidationError(
                    f"MUAC measurement and under-5 nutrition status (J04) are intended only for children under five years of age (current age: {rec.age} years)."
                )

    @api.constrains("uasc_status", "age")
    def _check_uasc_status(self):
        """
        [I02] Validates that adults (age >= 18) are not classified as unaccompanied
        or separated children.
        """
        for rec in self:
            if rec.uasc_status in ("unaccompanied", "separated") and rec.age >= 18:
                raise ValidationError(
                    f"Adult individual (age {rec.age} >= 18) cannot be designated as Unaccompanied or Separated Child (I02)."
                )

    @api.constrains("caregiver_individual_id", "caregiver_relationship")
    def _check_caregiver(self):
        """
        [I03] Validates caregiver references: an individual cannot be their own caregiver,
        and caregiver relationship must be documented.
        """
        for rec in self:
            if rec.caregiver_individual_id and rec.caregiver_individual_id.id == rec.id:
                raise ValidationError("An individual cannot be recorded as their own caregiver (I03).")
            if rec.caregiver_individual_id and not rec.caregiver_relationship:
                raise ValidationError("Caregiver relationship must be recorded when assigning a caregiver (I03).")

    @api.constrains("vulnerability_score")
    def _check_vulnerability_score(self):
        """
        [M02] Validates vulnerability score range 0 to 100.
        """
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

    @api.constrains("school_enrolment", "age")
    def _check_school_enrolment_age(self):
        """
        [K02] Validates that school enrolment is defined strictly for school-age children (6–17 years)
        according to the data dictionary specification.
        """
        for rec in self:
            if rec.school_enrolment and not (6 <= rec.age <= 17):
                raise ValidationError(
                    f"School enrolment (K02) is defined strictly for school-age children aged 6 to 17 years according to the data dictionary (current age: {rec.age} years)."
                )

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
        [Q01, Q02] Validates that closing a record requires closure reason and date.
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
