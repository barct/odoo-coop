# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
from debug import oprint

from utils import doc_number_normalize, name_clean
from suscriber import Suscriber


class IngresosMember(models.Model, Suscriber):
    _name = "infocoop.ingresos_member"

    master_id = fields.Many2one('infocoop_ingresos', ondelete='cascade')
    slave_id = fields.Many2one('res.partner')

    mirror_dependencies = ["infocoop_ingresos", "infocoop_tablas"]

    def prepare_row_fields(self, row):

        sm = self.env["infocoop_socios_member"].search(
            [("master_id", "=", row.id), ], limit=1)
        if sm:
            data = sm.prepare_row_fields(row)
        else:

            doc_type, doc_number = doc_number_normalize(
                row.tipo_doc, row.nro_doc)

            # TODO: This could be more efficient
            ids = self.env["afip.document_type"].search(
                (["active", "=", True], ["code", "=", doc_type]), limit=1)
            if ids:
                doc_type = ids[0].id
            else:
                doc_type = None

            minutes_id = None
            if row.acta:
                minutes_id = self.env["minutes"].search(
                    (["number", "=", row.acta],), limit=1).id
                if not minutes_id:
                    minutes_id = self.env["minutes"].create(
                        {"number": row.acta, "date": row.fec_acta}).id

            localidad = self.env["infocoop_tablas"].search(
                (["tema", "=", "T"], ["subtema", "=", "L"], ["codigo", "=", row.localidad]), limit=1)
            if localidad:
                city = localidad["concepto"].title()
            else:
                city = None

            # TODO: This could be more efficient
            responsability_id = self.env["afip.responsability"].search(
                (["name", "=", "Consumidor Final"], ["active", "=", 1]), limit=1).id

            data = {
                "name": name_clean(row.nombre),
                "document_number": doc_number,
                "document_type_id": doc_type,
                "birthdate": row.fec_nacim,
                "affiliation_date": row.fec_ingr,
                "membership_number": row.socio,
                "phone": row.telefono,
                "comment": row.observacio,
                "admission_minutes_id": minutes_id,
                "city": city,
                "street": row.domicilio,
                "zip": row.codpostal,
                "responsability_id": responsability_id,
            }
        return data

    def get_slave_from_row(self, row):
        if row.socio > 0:
            return self.env[self.slave_id._name].search([("membership_number", "=", row.socio), ], limit=1)
        else:
            return None
