# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
import datetime
import os

class infocoop_mirror_tables(models.Model):
	_name = 'infocoop.mirror_tables'

	name = fields.Char("Name")
	dbf_file = fields.Char("DBF file")
	
	file_modified = fields.Datetime("File Modified", compute='get_file_modified')
	last_sync = fields.Datetime("Last Sync")
	records = fields.Integer("Records", compute='get_records')
	out_of_date = fields.Boolean("Out of Date", compute='get_out_of_date')


	@api.one
	def get_file_modified(self):
		path = self.env["infocoop_configuration"].get_dbf_path()
		dt = os.path.getmtime(path + "/" + self.dbf_file)
		self.file_modified = datetime.datetime.fromtimestamp(dt)

	@api.one
	def get_records(self):
		count = self.env[self.name].search_count([])
		self.records = count

	@api.multi
	def sync_selected(self):
		
		for mt in self:
			self.env[mt.name].sync()
			mt.last_sync = datetime.datetime.now()

	@api.one
	def get_out_of_date(self):
		self.out_of_date = (self.last_sync<=self.file_modified)

	


class infocoop_suscribe_tables(models.Model):
	_name = 'infocoop.suscribe_tables'
	_order = 'sequence'

	name = fields.Char("Name")
	sequence = fields.Integer("Sequence")

	last_total_sync = fields.Datetime("Last Total Sync")
	records = fields.Integer("Records", compute='get_records')
	outs_of_date = fields.Integer("Out of Date", compute='get_outs_of_date')



	@api.one
	def get_file_modified(self):
		path = self.env["infocoop_configuration"].get_dbf_path()
		dt = os.path.getmtime(path + "/" + self.dbf_file)
		self.file_modified = datetime.datetime.fromtimestamp(dt)

	@api.one
	def get_records(self):
		self.records = self.env[self.name].search_count([])

	@api.one
	def get_outs_of_date(self):
		count = 0
		for e in self.env[self.name].search([]): 
			if e.master_id.hashcode!=e.hashcode:
				count+=1

		self.outs_of_date = count

	@api.multi
	def sync_selected(self):
		for st in self:
			self.env[st.name].sync_to_odoo()
			st.last_total_sync = datetime.datetime.now()

	#@api.one
	#def get_out_of_date(self):
	#	self.out_of_date = (self.last_sync<=self.file_modified)