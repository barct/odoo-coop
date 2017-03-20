# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api


class Sector(models.Model):
    _name = "electric_utility.sector"

    code = fields.Char("Code", length=7)
    name = fields.Char("Name")

    _sql_constraints = [
        ('sector_unique_keys', 'unique(code)', 'Code must be unique!'), ]


class City(models.Model):
    _name = "electric_utility.city"
    name = fields.Char("City")

    tax_ids = fields.Many2many("account.tax", string="Municipal Taxes")


class Connection(models.Model):
    _name = "electric_utility.connection"

    number = fields.Integer("Connection N°", required=True)
    sector_id = fields.Many2one(
        "electric_utility.sector", "Sector", required=True)
    measurement_sequence = fields.Float("Measurement Sequence")
    meter_serial_number = fields.Char("Meter Serial Number")
    meter_brand = fields.Char("Meter Brand")
    meter_type = fields.Selection(string="Meter Type", selection=[
                                  ('A', 'Analogic'), ('D', 'Digital')])
    meter_installation_date = fields.Date("Meter Installation Date")

    service_address_street = fields.Char("Street")
    service_address_neighborhood = fields.Char("Neighborhood")
    service_address_city = fields.Many2one("electric_utility.city", "City")
    service_address_reference = fields.Text("Reference")
    service_address_lat = fields.Float("Latitude", digits=(3, 8))
    service_address_lng = fields.Float("Longitude", digits=(3, 8))
    cadastral_nomenclature = fields.Char("Cadastral Nomenclature")

    contrat_ids = fields.One2many(
        "electric_utility.contrat", "connection_id", string="Contrats")

    @api.multi
    def name_get(self):
        super(Connection, self).name_get()
        data = []
        for o in self:
            data.append((o.id, "%s %s" % (o.sector_id.code.rjust(
                2, "0"), str(o.number).rjust(5, "0"),)))
        return data

    _sql_constraints = [
        ('connection_unique_keys', 'unique(number)', 'Code must be unique!'), ]


class BillingGroup(models.Model):
    _name = "electric_utility.billing_group"

    code = fields.Char("Code", length=7)
    name = fields.Char("Name")

    _sql_constraints = [
        ('connection_unique_keys', 'unique(code)', 'Code must be unique!'), ]


class Invoice(models.Model):
    _inherit = "account.invoice"
    contrat_id = fields.Many2one("electric_utility.contrat", string="Contrat")


class Contrat(models.Model):

    _name = "electric_utility.contrat"

    date_start = fields.Date("Date Start", required=True)
    date_end = fields.Date("Date End")

    connection_id = fields.Many2one(
        "electric_utility.connection", string="Connection", required=True)
    contrat_number = fields.Char("Contrat N°", length=7)
    client_id = fields.Many2one("res.partner", string="Client", required=True)

    service_category_id = fields.Many2one(
        "electric_utility.service_category",
        string="Service Category", required=True)
    service_status = fields.Selection(string="Service Status",
                                      selection=[(1, 'Normal'),
                                                 (2, 'In Cutlist'),
                                                 (3, 'Suspended'),
                                                 (4, 'Inactive')],
                                      default=0)
    installed_potency = fields.Integer("Installed Potency", default=5)

    billing_sequence = fields.Float("Billing Sequence")
    billing_group_id = fields.Many2one(
        "electric_utility.billing_group", string="Billing Group")

    billing_address_street = fields.Char("Street")
    billing_address_neighborhood = fields.Char("Neighborhood")
    billing_address_city = fields.Char("City")
    billing_address_zip = fields.Char("Zip", length=24)

    account_id = fields.Many2one("account.account", string="Account")

    comment = fields.Text("Comment")

    _sql_constraints = [
        ('connection_unique_keys',
         'unique(contrat_number)',
         'Code must be unique!'), ]

    @api.multi
    def name_get(self):
        super(Contrat, self).name_get()
        data = []
        for o in self:
            data.append((o.id, "%s - %s" %
                         (str(o.contrat_number).rjust(5, "0"),
                          o.client_id.name)))
        return data
