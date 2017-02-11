# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
from suscriber import Suscriber
#from debug import oprint
import datetime


_vars = {} 
def global_cache_var(env, var ,func):
	'''
	This function implement a cache to avoid repetitive access to the database
	'''
	global _vars
	if var in _vars:
		return _vars[var]
	else:
		_vars[var]=func(env)
		return _vars[var]



class LiquidacInvoice(models.Model, Suscriber):
	_name = "infocoop.liquidac_invoice"
	
	master_id = fields.Many2one('infocoop_liquidac', ondelete='cascade')
	slave_id = fields.Many2one('account.invoice')

	mirror_dependencies = ["infocoop_liquidac",]
	
	
	def prepare_row_fields(self, row):

		def env_ref(ref):
			'''
			This subfunction is a mask for global_cache_var
			'''
			return global_cache_var(
				env = self.env,
				var = ref,
				func = lambda env: env.ref(ref)
				)
		
		##get journal whit cache for efficiency 
		journal_id =  global_cache_var(self.env,"liquidac_invoice_journal_id",lambda env: env["infocoop_configuration"].get_liquidac_invoice_journal_id())
		if not journal_id:
			raise Exception("Liquidac to Invoice Journal must be configurated")

		#get client_id whit cache for efficiency 
		contrat = global_cache_var(
			env = self.env,
			var = "contrat"+str(row.medidor)+str(row.orden),
			func = lambda env: env["electric_utility.contrat"].search([("contrat_number","=",str(row.medidor)+str(row.orden)),],limit=1)
			)
		if contrat:
			partner_id = contrat.client_id
			commercial_partner = partner_id.commercial_partner_id 
		else:
			raise Exception("Contrat %s%s not found" % (row.medidor,row.orden))


		tab_fact =  global_cache_var(
			env = self.env,
			var = "tfact"+row.periodo,
			func = lambda env: env["infocoop.tab_fact"].search([("periodo","=",row.periodo),], limit=1)
			)

		#determine date invoice from periodo
		_sp =  row.periodo.split("/")
		month=int(_sp[0])
		year = int(_sp[1])
		if month in [2,4,6,8,10,12]: 
			date_invoice =  datetime.date(year=year, month=month-1, day=1)
		else:
			date_invoice = datetime.date(year=year, month=month, day=1)

		#get document type
		if commercial_partner.afip_responsability_type_id.code == 1:
			document_type_id = env_ref('l10n_ar_account.dc_a_ls')
		else:
			document_type_id = env_ref('l10n_ar_account.dc_b_ls')

		return {
		
		"date_invoice": date_invoice,
		"date_due": tab_fact.venc_1, 
		"journal_id": journal_id.id,

		"company_id": self.env.user.company_id.id,
		"currency_id": self.env.user.company_id.currency_id.id,
		"amount_untaxed": row.neto_serv,
		"amount_tax": row.neto_imp,
		"amount_total": row.neto_serv + row.neto_imp,
		"partner_id": partner_id.id,
		"commercial_partner_id": commercial_partner.id,
		
		"state": "draft",
		"account_id":journal_id.default_debit_account_id.id,
		#"type": "out_invoice",
		#"internal_number":  internal_number,
		"sent": False,
		#"period_id": period_id,
		"document_type_id": document_type_id.id,
		#"journal_document_type_id": journal_document_class.id,
		"document_number": row.num_fact[-12:-8].replace(" ","0") + "-" + row.num_fact[-8:],
		"contrat_id": contrat.id,
		
		"afip_responsability_type_id": partner_id.afip_responsability_type_id.id,

		}

	def finally_row_fields(self, row):
		def env_ref(ref):
			'''
			This subfunction is a mask for global_cache_var
			'''
			return global_cache_var(
				env = self.env,
				var = ref,
				func = lambda env: env.ref(ref)
				)
		invoice = self.slave_id
		self.env["account.invoice.line"].search([("invoice_id","=",invoice.id),]).unlink()
		self.env["account.invoice.tax"].search([("invoice_id","=",invoice.id),]).unlink()



		aux_ids = self.env["infocoop_auxiliar"].search(
			[("medidor","=",row["medidor"]),("orden","=",row["orden"]),("periodo","=",row["periodo"])]
			)

		
		auxee = 0
		comment = ""
		tax_list = list()
		line_pf_penal = None
		for aux in aux_ids:
			tax = None
			if aux.item in ("14","53","54"):
				auxee += aux.importe
				comment+=aux.concepto + " $" + str(aux.importe*-1) + "\n\r"
			elif aux.item in  ["5","15"]: #sepelio
				product = env_ref('funeral_insurance.product_product_funeral_insurance')
				data = dict()
				data["invoice_id"] = invoice.id
				data["product_id"] =  product.id
				data["price_unit"] =  aux.importe
				data["name"] = aux.concepto
				data["account_id"] = product.product_tmpl_id.property_account_income_id.id
				data["quantity"] = 1
				line = self.env["account.invoice.line"].create(data)
				line.invoice_line_tax_ids=[(4, env_ref('l10n_ar_chart.ri_tax_vat_no_corresponde_ventas').id)]

			elif aux.item=="32": #Power Factor Penalty
				product = env_ref('electric_utility.product_product_electric_service_power_factor_penalty')
				data = dict()
				data["invoice_id"] = invoice.id
				data["product_id"] =  product.id
				data["price_unit"] =  aux.importe
				data["name"] = aux.concepto
				data["account_id"] = product.product_tmpl_id.property_account_income_id.id
				data["quantity"] = 1
				line_pf_penal = self.env["account.invoice.line"].create(data)
				auxee -= aux.importe

			elif aux.item == "50": # COIE
				tax = env_ref("ersep_regulations.ersep_tax_coie")
			elif aux.item == "49": # ctoidnnp
				tax = env_ref("ersep_regulations.ersep_tax_ctoidnnp")
			elif aux.item == "51": # Tasa Seguridad eléctrica
				tax = env_ref("ersep_regulations.ersep_tax_seguridad_electrica")
			elif aux.item == "16": # Arroyo Cabral
				tax = env_ref("ersep_regulations.ersep_tax_arroyo_cabral")
			elif aux.item == "7": # Fuego
				tax = env_ref("ersep_regulations.ersep_tax_fuego")
			elif aux.item == "8": # ersep_tax_inf_electrica
				tax = env_ref("ersep_regulations.ersep_tax_inf_electrica")
			elif aux.item == "6": # ersep_tax_inf_electrica
				tax = env_ref("ersep_regulations.ersep_tax_ersep")
				
			if tax:
				data = dict()
				data["invoice_id"] = invoice.id
				data["tax_id"] =  tax.id
				data["amount"] =  aux.importe
				data["name"] = aux.concepto
				data["account_id"] = tax.account_id.id
				#create an append tax line
				tax_line = self.env["account.invoice.tax"].create(data)
				tax_list.append(tax_line.tax_id.id)

		#save discount coment 
		if comment:
			invoice.comment=comment


		#vat
		if row["iva2"]>0:
			tax = env_ref('l10n_ar_chart.ri_tax_vat_27_ventas')
			vat=row["iva2"]
		else:
			tax = env_ref('l10n_ar_chart.ri_tax_vat_21_ventas')
			vat=row["iva1"]
		data = dict()
		data["invoice_id"] = invoice.id
		data["tax_id"] =  tax.id
		data["amount"] =  vat
		data["name"] = tax.name
		data["account_id"] = tax.account_id.id
		tax_line = self.env["account.invoice.tax"].create(data)
		tax_list.append(tax_line.tax_id.id)

		
		#TODO: if discount id gether than cargo_fijo + imp_ee?

		#product_product_electric_service_flat_fee
		product = env_ref('electric_utility.product_product_electric_service_flat_fee')
		data = dict()
		data["invoice_id"] = invoice.id
		data["product_id"] =  product.id
		data["price_unit"] =  row["cargo_fijo"]
		data["name"] = product.name
		data["account_id"] = product.product_tmpl_id.property_account_income_id.id
		data["quantity"] = 1
		line_flat = self.env["account.invoice.line"].create(data)


		#product_product_electric_service_consumption
		product = env_ref('electric_utility.product_product_electric_service_consumption')
		data = dict()
		data["invoice_id"] = invoice.id
		data["product_id"] =  product.id
		data["price_unit"] =  row["imp_ee"]+auxee
		#data["discount"] = discount
		data["name"] = product.name
		data["account_id"] = product.product_tmpl_id.property_account_income_id.id
		data["quantity"] = 1
		line_cons = self.env["account.invoice.line"].create(data)


		for tax in invoice.contrat_id.connection_id.service_address_city.tax_ids:
			data = dict()
			data["invoice_id"] = invoice.id
			data["tax_id"] =  tax.id
			data["amount"] =  row["rec_muni"]
			data["name"] = tax.name
			data["account_id"] = tax.account_id.id
			tax_line = self.env["account.invoice.tax"].create(data)
			tax_list.append(tax_line.tax_id.id)

		line_flat.invoice_line_tax_ids=[(6,0, tax_list)]
		line_cons.invoice_line_tax_ids=[(6,0, tax_list)]
		if line_pf_penal:
			line_pf_penal.invoice_line_tax_ids=[(6,0, tax_list)]


		#invoice.action_date_assign()
		invoice.action_move_create()
		invoice.invoice_validate()







	def get_slave_form_row(self, row):		
		return self.env["account.invoice"].search([("document_number","=",row.num_fact[-12:-8].replace(" ","0") + "-" + row.num_fact[-8:]),], limit=1)	

	