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
    nationality = fields.Char(string="Nationality")
    country_of_origin = fields.Char(string="Country of Origin")
    legal_status = fields.Char(string="Legal Status")
    presence_status = fields.Char(string="Presence Status")
    record_status = fields.Char(string="Record Status")
    arrival_date = fields.Date(string="Arrival Date")
    address_line_1 = fields.Char(string="Address Line 1")
    country_code = fields.Char(string="Country Code")
