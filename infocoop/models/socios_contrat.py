# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields  # , api
from suscriber import Suscriber
from datetime import date


class SociosConnection(models.Model, Suscriber):

    _name = "infocoop.socios_contrat"

    master_id = fields.Many2one('infocoop_socios', ondelete='cascade')
    slave_id = fields.Many2one('electric_utility.contrat')

    mirror_dependencies = ["infocoop_socios", "infocoop_tablas",
                           "infocoop_red_usu", "infocoop_ingresos",
                           "infocoop_modi_soc", ]

    def prepare_row_fields(self, row):
        # look for good start date
        if row.fec_inen:
            date_start = row.fec_inen
        else:
            ingresos = self.env["infocoop_ingresos"].search(
                [("medidor", "=", row.medido), ("orden", "=", row.orden)],
                limit=1)
            if ingresos and ingresos.fec_ingr:
                date_start = ingresos.fec_ingr
            else:
                red_usu = self.env["infocoop_red_usu"].search(
                    [("medidor", "=", row.medido), ("orden", "=", row.orden)],
                    limit=1)
                if red_usu and red_usu.fec_inst:
                    date_start = red_usu.fec_inst
                else:
                    modi_soc = self.env["infocoop_modi_soc"].search(
                        [("medidor", "=", row.medido),
                         ("orden", "=", row.orden),
                         ("campo", "=", "ACTIVO"),
                         ("actual", "=", "S")],
                        order="fecha desc, hora desc", limit=1)
                    if modi_soc:
                        date_start = modi_soc.fecha
                    else:
                        modi_soc = self.env["infocoop_modi_soc"].search(
                            [("medidor", "=", row.medido),
                             ("orden", "=", row.orden)],
                            order="fecha desc, hora desc", limit=1)
                        if modi_soc:
                            date_start = modi_soc.fecha
                        else:
                            date_start = date(1111, 11, 11)

        # calculate service status
        if row.activo == "S" and (row.corte == "N" or not row.corte):
            service_status = 1
        elif row.activo == "S" and row.corte == "S":
            service_status = 3
        else:
            service_status = 4

        date_end = None
        modi_soc = self.env["infocoop_modi_soc"].search(
            [("medidor", "=", row.medido),
             ("orden", "=", row.orden),
             ("campo", "=", "ACTIVO")],
            order="fecha desc, hora desc", limit=1)
        if modi_soc.actual == "N" and service_status not in (1, 2):
            date_end = modi_soc.fecha
        elif service_status > 2 and modi_soc.fecha:
            date_end = modi_soc.fecha
        elif service_status == 4 and not modi_soc:
            modi_soc = self.env["infocoop_modi_soc"].search(
                [("medidor", "=", row.medido),
                 ("orden", "=", row.orden)],
                order="fecha desc, hora desc", limit=1)
            if modi_soc:
                date_end = modi_soc.fecha

        connection = self.get_or_create_connection(row)
        client = self.get_or_create_client(row)
        service_category = self.get_or_create_service_category(row)

        # Transform Sequence String to Float
        if row.secuencia:
            seq_first = row.secuencia[:6]
            seq_rest = row.secuencia[6:]
            try:
                int_part = int(seq_first)
            except:
                int_part = 0
            n = ""
            for e in seq_rest:
                n += str(ord(e))
            sequence = float(int_part) + float("0." + n)
        else:
            sequence = None

        # obtein billing group
        if row.codint:
            billing_group_id = self.env["electric_utility.billing_group"].\
                search([("code", "=", row.codint), ], limit=1).id
            if not billing_group_id:
                billing_group_id = self.env["electric_utility.billing_group"].\
                    create({"code": row.codint, "name": row.codint}).id
        else:
            billing_group_id = None

        # get or create city
        city = self.env["infocoop_tablas"].search((
            ["tema", "=", "T"],
            ["subtema", "=", "L"],
            ["codigo", "=", row.codloca]), limit=1)
        if city:
            city = city["concepto"].title()
        else:
            city = None

        # split address in street and neighborhood
        if row.direccion:
            address_split = row.direccion.split("-")
            if len(address_split) > 1:
                street = "".join(address_split[:-1]).strip()
                neighborhood = address_split[-1].strip()
            else:
                street = row.direccion.strip()
                neighborhood = None
        else:
            street = None
            neighborhood = None

        data = {"date_start": date_start,
                "date_end": date_end,
                "connection_id": connection.id,
                "client_id": client.id,
                "contrat_number": str(row.medido) + str(row.orden),
                "service_category_id": service_category.id,
                "billing_sequence": sequence,
                "billing_group_id": billing_group_id,
                "billing_address_street": street,
                "billing_address_neighborhood": neighborhood,
                "billing_address_city": city,
                "billing_address_zip": row.codpostal,
                "service_status": service_status,
                }
        return data

    def get_slave_from_row(self, row):
        return self.env[self.slave_id._name].search(
            [("contrat_number", "=", str(row.medido) + str(row.orden)), ],
            limit=1)

    def get_or_create_connection(self, row):
        sc = self.env["infocoop.socios_connection"].sync_row(row)
        if sc:
            return sc.slave_id
        else:
            return None

    def get_or_create_client(self, row):
        sm = self.env["infocoop.socios_member"].sync_row(row)
        if sm:
            return sm.slave_id
        else:
            return None

    def get_or_create_service_category(self, row):
        # TODO: change this for ref to data xml
        if row.catene in (1, 21):
            code = "E1"
            ersep_code = "T1.1"
            name = "Residencial"
        elif row.catene in (2, 4, 22, 24):
            code = "E2"
            ersep_code = "T2.2"
            name = "Industrial"
        elif row.catene in (3, 23):
            code = "E3"
            ersep_code = "T7.1"
            name = "Alumbrado Público"
        elif row.catene in (5, 6, 25, 26):
            code = "E6"
            ersep_code = "T2.1"
            name = "Comercial"
        elif row.catene in (7, 27):
            code = "E7"
            ersep_code = "T5.1"
            name = "Rural"
        elif row.catene in (8, 28):
            code = "E8"
            ersep_code = "T6.1"
            name = "Sector Público"
        elif row.catene in (9, 29):
            code = "E9"
            ersep_code = "T6.1"
            name = "Comercial Combinada"
        elif row.catene in (10, 30):
            code = "E10"
            ersep_code = "T1.8"
            name = "Residencial Estacional"
        elif row.catene == 11:
            code = "E11"
            ersep_code = "T3.1.1"
            name = "Demanda Contratada"
        else:
            code = "E0"
            ersep_code = None
            name = "(desconocido)"

        sc = self.env["electric_utility.service_category"].search(
            [("code", "=", code), ],
            limit=1)
        if sc:
            return sc
        else:
            return self.env["electric_utility.service_category"].create({
                "code": code, "ersep_code": ersep_code, "name": name})
