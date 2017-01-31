# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
from debug import oprint

from utils import doc_number_normalize, name_clean, insert_or_update
import utils
from suscriber import Suscriber
import re


class SociosMember(models.Model, Suscriber):
	_name = "infocoop.socios_member"
	
	master_id = fields.Many2one('infocoop_socios', ondelete='cascade')
	slave_id = fields.Many2one('res.partner')

	mirror_dependencies = ["infocoop_socios","infocoop_tablas","infocoop_suscrip","infocoop_ingresos",]


	def prepare_row_fields(self, row):
		if not row:
			raise Exception("%s: row %s no válida" % (self._name,row))

		data={}
		doc_number = None
		doc_type=None
		if row.cuit:
			doc_type = self.env["res.partner.id_category"].search((["active","=",True],["code","=","CUIT"]), limit=1)
			doc_number = re.sub('[-]','',row.cuit)


		localidad = self.env["infocoop_tablas"].search((["tema","=","T"],["subtema","=","L"],["codigo","=",row.codloca]), limit=1)
		if localidad:
			city = localidad["concepto"].title()
		else:
			city = None

	
		minutes_id = None
		gender = None
		ingreso = self.env["infocoop_ingresos"].search([("socio","=",row.nrosoc),],limit=1)
		if ingreso:
			minutes_id = self.env["minutes"].search((["number","=",ingreso.acta],), limit=1).id
			if not minutes_id:
				minutes_id= self.env["minutes"].create({"number":ingreso.acta, "date":ingreso.fec_acta}).id

			if not doc_number:
				#get doc data from ingresos
				doc_type, doc_number = doc_number_normalize(ingreso.tipo_doc, ingreso.nro_doc)
		
				ids = self.env["res.partner.id_category"].search((["active","=",True],["code","=",doc_type]), limit=1)
				if ids:
					doc_type=ids[0]
				else:
					doc_type=None

			if ingreso.sexo=="M": data["gender"] = "male"
			elif ingreso.sexo == "F": data["gender"] = "female"

			data["birthdate"] = ingreso.fec_nacim


		if doc_type:
			try: 
				doc_type.validate_id_number(doc_number)
				doc_type=doc_type.id
			except:
				data["comment"]="Identity validation fail: %s %s " % (doc_type, doc_number)
				doc_type=None


			data["affiliation_date"]=ingreso.fec_ingr
			data["membership_number"]=row.nrosoc
			data["admission_minutes_id"]=minutes_id
			data["disaffiliation_date"] = ingreso.fec_baja

		#TODO: This could be more efficient
		code = utils.afip_resposability_equivalences(row.codiva)
		responsability_id = self.env["afip.responsability.type"].search((["code","=",code],["active","=",1]), limit=1).id
		if code == "1" or code == "4": #RI or Exento
			data["is_company"] = True

		susc = self.env["infocoop_suscrip"].search([("nrosoc","=",row.nrosoc),], limit=1)
		if susc:
			data["subscribed_share_capital"] = susc.capital
			data["subscribed_share_capital_cert_number"] = susc.nro_cert
			data["subscribed_share_capital_date"] = susc.fecha

		if row.nombre:
			data["name"] = name_clean(row.nombre)
		else:
			data["name"] = "(desconocido)"
		
		data["main_id_number"]=doc_number
		data["main_id_category_id"]=doc_type
		data["phone"]=row.telefono
		data["comment"]=row.observacio
		
		data["city"]=city
		data["street"]=row.direccion
		data["zip"]=row.codpostal
		data["afip_responsability_type_id"]=responsability_id
		data["gender"]=gender

		return data

	# def finally_row_fields(self, row):
	# 	#self.slave_id

	# 	doc_number = None
	# 	doc_type=None
	# 	if row.cuit:
	# 		doc_type = self.env["res.partner.id_category"].search((["active","=",True],["code","=","CUIT"]), limit=1).id
	# 		doc_number = re.sub('[-]','',row.cuit)

	# 		insert_or_update(
	# 				env=self.env,
	# 				model="res.partner.id_number",
	# 				constraints={"partner_id":self.slave_id.id, "category_id":doc_type},
	# 				data={"name": doc_number })

		
	# 	#get doc data from ingresos
	# 	ingreso = self.env["infocoop_ingresos"].search([("socio","=",row.nrosoc),],limit=1)
	# 	if ingreso:
	# 		doc_type, doc_number = doc_number_normalize(ingreso.tipo_doc, ingreso.nro_doc)
	# 		ids = self.env["res.partner.id_category"].search((["active","=",True],["code","=",doc_type]), limit=1).id
	# 		if ids:
	# 			doc_type=ids
	# 			insert_or_update(
	# 			env=self.env,
	# 			model="res.partner.id_number",
	# 			constraints={"partner_id":self.slave_id.id, "category_id":doc_type},
	# 			data={"name": doc_number })
				




	def get_slave_form_row(self, row):
		socio = self.env["infocoop_ingresos"].search([("socio","=",row.nrosoc),], limit=1).socio
		if socio>0:
			return self.env[self.slave_id._name].search([("membership_number","=",socio),], limit=1)
		else:
			return None