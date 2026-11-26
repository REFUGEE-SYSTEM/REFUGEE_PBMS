from odoo import fields, models


class G2PRegisterRefugees(models.Model):
    _name = "g2p.register.refugees"
    _table = "g2p_register_refugees"
    _auto = False
    _description = "Refugee Register (PBMS Metadata)"

    internal_record_id = fields.Char(string="Internal Record ID")
    functional_record_id = fields.Char(string="Functional Record ID")
    foundational_id = fields.Char(string="Foundational ID")
    record_name = fields.Char(string="Full Name")
    first_name = fields.Char(string="First Name")
    middle_name = fields.Char(string="Middle Name")
    last_name = fields.Char(string="Last Name")
    gender = fields.Char(string="Gender")
    birth_date = fields.Date(string="Birth Date")
    is_birth_date_estimated = fields.Boolean(string="Birth Date Estimated")
    place_of_birth = fields.Char(string="Place of Birth")
    nationality = fields.Char(string="Nationality")
    country_of_origin = fields.Char(string="Country of Origin")
    legal_status = fields.Char(string="Legal Status")
    rsd_application_date = fields.Date(string="RSD Application Date")
    security_screening_status = fields.Char(string="Security Screening Status")
    presence_status = fields.Char(string="Presence Status")
    unaccompanied_separated_status = fields.Char(string="Unaccompanied/Separated Status")
    marital_status = fields.Char(string="Marital Status")
    occupation = fields.Char(string="Occupation")
    income_level = fields.Char(string="Income Level")
    education_level = fields.Char(string="Education Level")
    highest_education_level = fields.Char(string="Highest Education Level")
    religion = fields.Char(string="Religion")
    record_status = fields.Char(string="Record Status")
    lifecycle_status = fields.Char(string="Lifecycle Status")
    arrival_date = fields.Date(string="Arrival Date")
    registration_date = fields.Date(string="Registration Date")
    enrolment_date = fields.Date(string="Enrolment Date")
    exit_date = fields.Date(string="Exit Date")
    exit_reason = fields.Char(string="Exit Reason")
    address_line_1 = fields.Char(string="Address Line 1")
    address_line_2 = fields.Char(string="Address Line 2")
    postal_code = fields.Char(string="Postal Code")
    country_code = fields.Char(string="Country Code")

    # Washington Group disability & medical fields
    wg_seeing = fields.Char(string="WG Seeing")
    wg_hearing = fields.Char(string="WG Hearing")
    wg_walking = fields.Char(string="WG Walking")
    wg_remembering = fields.Char(string="WG Remembering")
    wg_self_care = fields.Char(string="WG Self Care")
    wg_communicating = fields.Char(string="WG Communicating")
    has_serious_medical_condition = fields.Boolean(string="Has Serious Medical Condition")
    programmes_enrolled = fields.Char(string="Programmes Enrolled")
