# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
from suscriber import Suscriber
from debug import oprint
import datetime


from utils import doc_number_normalize, name_clean


class LiquidacInvoice(models.Model, Suscriber):
	_name = "infocoop.liquidac_invoice"
	
	master_id = fields.Many2one('infocoop_liquidac', ondelete='cascade')
	slave_id = fields.Many2one('account.invoice')

	mirror_dependencies = ["infocoop_liquidac",]
	
	
	def prepare_row_fields(self, row):
		
		##get journal
		journal_id = self.env["infocoop_configuration"].get_liquidac_invoice_journal_id()
		if not journal_id:
			raise Exception("Liquidac to Invoice Journal must be configurated")

		#get client_id
		contrat = self.env["electric_utility.contrat"].search([("contrat_number","=",str(row.medidor)+str(row.orden)),],limit=1)
		if contrat:
			partner_id = contrat.client_id
		else:
			raise Exception("Contrat %s%s not found" % (row.medidor,row.orden))

		#desagrego periodo
		_sp =  row.periodo.split("/")
		month=int(_sp[0])
		year = int(_sp[1])
		period_date = datetime.date(year=year, month=month, day=1)
		#period_id = self.env["account.period"].search([("date_start","<=",period_date),],limit=1, order="date_start desc").id

		#internal_number = "DV/2016/" + str(row.numero), #TODO: get journal book
		document_type_id = self.env.ref('l10n_ar_account.dc_b_ls')
		#journal_document_class = self.env["account.journal.afip_document_class"].search([("afip_document_class_id","=",afip_document_class.id),],limit=1)

		#prefix = journal_id.sequence_id.prefix

		#sequence = journal_id.sequence_id
		#d = sequence._interpolation_dict()
		#interpolated_prefix = sequence._interpolate(sequence['prefix'], d)
		#interpolated_suffix = sequence._interpolate(sequence['suffix'], d)
		#internal_number = interpolated_prefix + '%%0%sd' % sequence['padding'] % row.numero + interpolated_suffix

		return {
		#"number": internal_number , #TODO: get journal book
		#"supplier_invoice_number": internal_number,
		"date_invoice": period_date, # TODO: find in tabla_fact
		"date_due": None, # TODO: find in tabla_fact
		"journal_id": journal_id.id,

		"company_id": self.env.user.company_id.id,
		"currency_id": self.env.user.company_id.currency_id.id,
		"amount_untaxed": row.neto_serv,
		"amount_tax": row.neto_imp,
		"amount_total": row.neto_serv + row.neto_imp,
		"partner_id": partner_id.id,
		"commercial_partner_id": partner_id.id,
		
		"state": "draft",
		"account_id":journal_id.default_debit_account_id.id,
		#"type": "out_invoice",
		#"internal_number":  internal_number,
		"date_invoice": period_date, ##TODO: get from settlements
		"sent": False,
		#"period_id": period_id,
		"document_type_id": document_type_id.id,
		#"journal_document_type_id": journal_document_class.id,
		"document_number": row.num_fact[8:],
		"contrat_id": contrat.id,
		
		"afip_responsability_type_id": partner_id.afip_responsability_type_id.id,

		}

	def finally_row_fields(self, row):
		invoice = self.slave_id
		self.env["account.invoice.line"].search([("invoice_id","=",invoice.id),]).unlink()
		self.env["account.invoice.tax"].search([("invoice_id","=",invoice.id),]).unlink()



		aux_ids = self.env["infocoop_auxiliar"].search(
			[("medidor","=",row["medidor"]),("orden","=",row["orden"]),("periodo","=",row["periodo"])]
			)

		
		discount = 0
		comment = ""
		tax_list = list()
		for aux in aux_ids:
			tax = None
			if aux.item in ("14","53","54"):
				discount += aux.importe*-1
				comment+="Descuento: " + aux.concepto + " $" + str(aux.importe*-1) + "\n\r"
			elif aux.item in  ["5","15"]: #sepelio
				product = self.env.ref('funeral_insurance.product_product_funeral_insurance')
				data = dict()
				data["invoice_id"] = invoice.id
				data["product_id"] =  product.id
				data["price_unit"] =  aux.importe
				data["name"] = aux.concepto
				data["account_id"] = product.product_tmpl_id.property_account_income_id.id
				data["quantity"] = 1
				line = self.env["account.invoice.line"].create(data)

				line.invoice_line_tax_ids=[(4, self.env.ref('l10n_ar_chart.ri_tax_vat_no_corresponde_ventas').id)]

				

			elif aux.item == "50": # COIE
				tax = self.env.ref("ersep_regulations.ersep_tax_coie")
			elif aux.item == "49": # ctoidnnp
				tax = self.env.ref("ersep_regulations.ersep_tax_ctoidnnp")
			elif aux.item == "51": # Tasa Seguridad eléctrica
				tax = self.env.ref("ersep_regulations.ersep_tax_seguridad_electrica")
			elif aux.item == "16": # Arroyo Cabral
				tax = self.env.ref("ersep_regulations.ersep_tax_arroyo_cabral")
			elif aux.item == "7": # Fuego
				tax = self.env.ref("ersep_regulations.ersep_tax_fuego")
			elif aux.item == "8": # ersep_tax_inf_electrica
				tax = self.env.ref("ersep_regulations.ersep_tax_inf_electrica")
				
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
			tax = self.env.ref('l10n_ar_chart.ri_tax_vat_27_ventas')
			vat=row["iva2"]
		else:
			tax = self.env.ref('l10n_ar_chart.ri_tax_vat_21_ventas')
			vat=row["iva1"]
		data = dict()
		data["invoice_id"] = invoice.id
		data["tax_id"] =  tax.id
		data["amount"] =  vat
		data["name"] = tax.name
		data["account_id"] = tax.account_id.id
		tax_line = self.env["account.invoice.tax"].create(data)
		tax_list.append(tax_line.tax_id.id)

		
		#product_product_electric_service_flat_fee
		product = self.env.ref('electric_utility.product_product_electric_service_flat_fee')
		data = dict()
		data["invoice_id"] = invoice.id
		data["product_id"] =  product.id
		data["price_unit"] =  row["cargo_fijo"]
		data["name"] = product.name
		data["account_id"] = product.product_tmpl_id.property_account_income_id.id
		data["quantity"] = 1
		line_flat = self.env["account.invoice.line"].create(data)


		#product_product_electric_service_consumption
		product = self.env.ref('electric_utility.product_product_electric_service_consumption')
		data = dict()
		data["invoice_id"] = invoice.id
		data["product_id"] =  product.id
		data["price_unit"] =  row["imp_ee"]
		data["discount"] = discount
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













	def get_slave_form_row(self, row):
		#desagrego periodo
		_sp =  row.periodo.split("/")
		month=int(_sp[0])
		year = int(_sp[1])
		period_date = datetime.date(year=year, month=month, day=1)
		
		return self.env["account.invoice"].search([("contrat_id.contrat_number","=",str(row.medidor)+str(row.orden)),("document_number","=",row.numero)], limit=1)	

	