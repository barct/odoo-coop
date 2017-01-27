# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
from suscriber import Suscriber
from psycopg2 import IntegrityError
from debug import oprint


from utils import doc_number_normalize, name_clean


class SociosConnection(models.Model, Suscriber):
	_name = "infocoop.socios_connection"
	
	master_id = fields.Many2one('infocoop_socios', ondelete='cascade')
	slave_id = fields.Many2one('electric_utility.connection')

	mirror_dependencies = ["infocoop_socios","infocoop_tablas","infocoop_red_usu"]

	def filter(self):
		return [("activo", "=", "S"),]
	
	
	def prepare_row_fields(self, row):
		#get or create sector
		sector_id = self.env["electric_utility.sector"].search([("code","=",row.barrio),], limit=1).id
		if not sector_id:
			sector_id = self.env["electric_utility.sector"].create({"code":row.barrio, "name": row.barrio}).id

		
		#get or create city
		city = self.env["infocoop_tablas"].search((["tema","=","T"],["subtema","=","L"],["codigo","=",row.codloca]), limit=1)
		if city:
			city = city["concepto"].title()
		else:
			city = None
		
		#split address in street and neighborhood
		if row.dirser:
			address_split = row.dirser.split("-")
			if len(address_split)>1:
				street = "".join(address_split[:-1]).strip()
				neighborhood = address_split[-1].strip()
			else:
				street = row.dirser.strip()
				neighborhood = None
		else:
			street = None
			neighborhood = None 


		#Transform Sequence String to Float
		if row.sec_estado:
			seq_first = row.sec_estado[:6]
			seq_rest =  row.sec_estado[6:]
			try:
				int_part = int(seq_first)
			except:
				int_part = 0
			n=""
			for e in seq_rest:
				n += str(ord(e))
			sequence = float(int_part)+float("0." + n)
		else:
			sequence = None

		
		
		data={"number": row.medido,
				"sector_id": sector_id,
				"measurement_sequence": sequence,
				"service_address_neighborhood": neighborhood,
				"service_address_street": street,
				"service_address_city": city,
				}


		#obtain meter data 
		red_usu = self.env["infocoop_red_usu"].search([("medidor","=",row.medido),("orden","=",row.orden)],limit=1)
		if red_usu.tipo_med >= 1:
			tipo_med = "D"
		else:
			tipo_med = "A"

		if red_usu:
			data["meter_serial_number"]=red_usu.nromedidor
			data["meter_brand"]=red_usu.marcamed
			data["meter_type"]=tipo_med
			data["meter_installation_date"]=red_usu.fec_inst
			data["service_address_lat"]=red_usu.latitud
			data["service_address_lng"]=red_usu.longitud
			data["cadastral_nomenclature"]=red_usu.desig_cat

		return data
	
	#def create_from_infocoop(self, row):	
	#	old = self.env[self.slave_id._name].search([("number","=",row.medido),], limit=1)
	#	if not old:
	#		new = self.env[self.slave_id._name].create((self.prepare_row_fields(row)))
	#		s = self.create({"slave_id":new.id, "master_id": row.id, "hashcode": row.hashcode})
#
#		return s 
			
	def get_slave_form_row(self, row):
		return self.env[self.slave_id._name].search([("number","=",row.medido),], limit=1)