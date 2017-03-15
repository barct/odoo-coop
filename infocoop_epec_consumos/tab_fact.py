# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
from openerp.osv import osv
from collections import OrderedDict


class infocoop_tab_fact(models.Model):
    _inherit = "infocoop_tab_fact"

class Values():
    code = "(desconocido)"
    conexiones = 1
    consumo = 0
    cargo_fijo = 0
    monto_ee = 0
    monto_ts = 0
    consumo_ts = 0
    monto_pe = 0
    consumo_pe = 0
    monto_impuestos = 0
    monto_otros = 0

    def __iadd__(self, vals):
        self.conexiones += vals.conexiones
        self.consumo += vals.consumo
        self.cargo_fijo += vals.cargo_fijo
        self.monto_ee += vals.monto_ee
        self.monto_ts += vals.monto_ts
        self.consumo_ts += vals.consumo_ts
        self.monto_pe += vals.monto_pe
        self.consumo_pe += vals.consumo_pe
        self.monto_impuestos += vals.monto_impuestos
        self.monto_otros += vals.monto_otros

        return self

    def __unicode__(self):
        txt = """code %s
            conexiones %s
            consumo: %s
            cargo_fijo: %s
            monto_ee: %s
            monto_ts: %s
            consumo_ts: %s
            monto_pe: %s
            consumo_pe: %s
            monto_impuestos: %s
            monto_otros: %s """
        return txt % (self.code,
                      self.conexiones,
                      self.consumo,
                      self.cargo_fijo,
                      self.monto_ee,
                      self.monto_ts,
                      self.consumo_ts,
                      self.monto_pe,
                      self.consumo_pe,
                      self.monto_impuestos,
                      self.monto_otros, )


class ParticularReport(models.AbstractModel):
    _name = 'report.infocoop_epec_consumos.report_example_report_view'

    def get_epec_data(self, docs):
        data = list()
        for r in docs:
            values = dict()
            liq_ids = self.env["infocoop_liquidac"].search([
                ("servicios", "=", "/E"),
                ("periodo", "=", r.periodo), ])
            for l in liq_ids:
                if l.service_category_id.group_id:
                    group, level = l.service_category_id.\
                        group_id.define_segment(l.cons_ee)
                else:
                    group = l.service_category_id.group_id.code
                    level = None

                v = Values()
                v.consumo = float(l.cons_ee)
                v.cargo_fijo = float(l.cargo_fijo)
                v.monto_ee = float(l.imp_ee)
                v.monto_impuestos = float(l.neto_imp)
                v.consumo_ts = float(l.ts_kwh)
                v.monto_ts = float(l.ts_amount)
                v.consumo_pe = float(l.pe_kwh)
                v.monto_pe = float(l.pe_amount)
                v.monto_otros = l.neto_serv - \
                    (v.monto_ee + v.cargo_fijo + v.monto_ts + v.monto_pe)
                code = None
                if l.service_category_id.group_id.code == "UR":
                    if l.pe_level == 2:
                        code = "5010"
                    elif l.pe_level == 3:
                        code = "5020"
                    elif l.ts_level == 2:
                        if l.cons_ee <= 150:
                            code = "5500"
                        else:
                            code = "5510"
                    elif l.ts_level == 1:
                        if l.cons_ee <= 150:
                            code = "5500"
                        elif l.cons_ee <= 450:
                            code = "5530"
                        else:
                            code = "5540"
                    else:
                        code = "5000"
                    v.code = group + str(level) + "-" + code
                else:
                    v.code = group + str(level)

                if v.code in values:
                    values[v.code] += v
                else:
                    values[v.code] = v

            data.append(
                {"doc": r,
                 "values": OrderedDict(sorted(values.items(),
                                              key=lambda t: t[0])), })
        return data

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(
            'infocoop_epec_consumos.report_example_report_view')
        docs = self.env['infocoop_tab_fact'].browse(self._ids)
        data = self.get_epec_data(docs)

        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': docs,
            'data': data,
        }
        return report_obj.render(
            'infocoop_epec_consumos.report_example_report_view', docargs)
