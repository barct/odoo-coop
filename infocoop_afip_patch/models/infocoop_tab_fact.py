# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
import base64
from afip_cesp import escribir, LIQUIDACION_SP
import datetime


class infocoop_tab_fact(models.Model):
    _inherit = "infocoop_tab_fact"

    cesp_data = fields.Binary(string='Cesp')
    cesp_filename = fields.Char()

    @api.one
    def generate_cesp(self):
        cesp_data = ""
        m1 = int(self.periodo[:2])
        y = int(self.periodo[-4:])
        p1 = self.periodo
        p2 = str(m1 + 1) + str(y)
        if m1 % 2 == 1:  # only even
            liqs = self.env["infocoop_liquidac"].search(
                [("periodo", "in", (p1, p2)), ])
            for l in liqs:
                socio_id = self.env["infocoop_socios"].search(
                    [("medido", "=", l.medidor), ("orden", "=", l.orden)],
                    limit=1)
                sm_ids = self.env["infocoop.socios_member"].search(
                    [("master_id", "=", socio_id.id), ], limit=1)

                if sm_ids:
                    partner_id = sm_ids.slave_id
                else:
                    ingreso_id = self.env["infocoop_ingresos"].search(
                        [("medidor", "=", l.medidor), ("orden", "=", l.orden)],
                        limit=1)
                    im_ids = self.env["infocoop.ingresos_member"].search(
                        [("master_id", "=", ingreso_id.id), ], limit=1)
                    partner_id = im_ids.slave_id

                print partner_id.name
                print partner_id.main_id_number

                vals = dict()
                vals['cbte_tipo'] = 18  # Liquidacion B
                vals['cbt_numero'] = l.numero
                vals['cbte_nro_interno'] = l.num_fact
                if l.servicios == "/A":
                    vals['tipo_servicio'] = "A"
                    vals['pto_vta'] = 3
                elif l.servicios == "/E":
                    vals['tipo_servicio'] = "E"
                    vals['pto_vta'] = 1
                else:
                    continue
                vals['fecha_cbte'] = datetime.date(
                    year=y, month=m1, day=1)

                # Usuario y tutular
                vals['usuario_tiene_info'] = 'S'
                vals['titular_tiene_info'] = 'S'
                vals['usuario_id'] = l.medidor + l.orden

                vals['usuario_nombre'] = socio_id.nombre
                vals['titular_nombre'] = socio_id.nombre

                if partner_id:
                    if partner_id.main_id_number\
                            and partner_id.main_id_category_id:
                        tipo_doc = \
                            partner_id.main_id_category_id.afip_code
                        if tipo_doc:
                            vals['usuario_tipo_doc'] = tipo_doc
                            vals['usuario_nro_doc'] = partner_id.main_id_number
                            vals['titular_tipo_doc'] = tipo_doc
                            vals['titular_nro_doc'] = partner_id.main_id_number

                    if partner_id.afip_responsability_type_id:
                        vals['usuario_impositiva_id'] = \
                            partner_id.afip_responsability_type_id.code
                # vals['titular_inmueble_tiene_info'] = 'N'


                # vals['usuario_domicilio_tiene_info'] = 'S'
                # vals['usuario_domicilio_calle']= l.prestacion.cliente.domicilio_particular.direccion    
                # vals['usuario_domicilio_puerta']=l.prestacion.cliente.domicilio_particular.altura
              
                # # vals=['usuario_domicilio_piso']=,  
                # # vals=['usuario_domicilio_oficina']=, 
                # vals['usuario_domicilio_cp']=prestacion.cliente.domicilio_particular.codigo_postal  
                # vals['usuario_domicilio_localidad']=prestacion.cliente.domicilio_particular.localidad.nombre
                # # vals=['usuario_domicilio_partido']=
                # vals['usuario_domicilio_provincia']=prestacion.cliente.domicilio_particular.provincia.codigo_afi
                cesp_data += escribir(vals, LIQUIDACION_SP)

        return self.write({
            'cesp_filename': 'cesp.txt',
            'cesp_data': base64.encodestring(cesp_data)
        })
