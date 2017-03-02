# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api, osv
from debug import oprint
from sys import stdout
from utils import doc_number_normalize, name_clean
from openerp.exceptions import Warning

class Suscriber():
	'''
		Suscriber class represent a subscription to a DBF mirror table of Infocoop
		Is responsible for maintaining sync data between a master record (infocoop mirror table row)
		and a slave record (business model)
	'''
	hashcode = fields.Char(length=10)
	_sql_constraints = [('unique_keys', 'unique(master_id,slave_id)', 'must be unique!'),]

	@api.multi
	def sync_to_odoo(self):
		'''
			Iterates all master records and update its corresponding slave records 
		'''
		#check if all mirror_dependencies are updated	
		deps=self.env["infocoop.mirror_tables"].search([("name","in",self.mirror_dependencies),])
		if deps:
			dep_str=""
			for d in deps:
				if d.out_of_date:
					dep_str+=d.name + ", "
			if dep_str!="":
				raise Warning("Out of date mirror_dependencies: %s" % dep_str)
		
		total = self.env[self.master_id._name].search_count(self.filter())
		count = 0
		ii_ids = self.env[self.master_id._name].search(self.filter())
		for row in ii_ids:
			self.sync_row(row)
			stdout.write("\r %s: %i de %i" % (self._name,count,total))
			stdout.flush()
			count += 1
	
	
	def sync_row(self, row):
		'''
			Check if slave record should be updated, deleted or created based on a master row
			and does it
		'''
		s_ids = self.env[self._name].search((["master_id","=",row.id],), limit=1)
		if s_ids:
			if row.sync_delete_mark:
				if not s_ids.slave_id is None:
					s_ids.delete_from_infocoop(row)
			else:
				if s_ids.slave_id is None:
					slave = self.get_slave_from_row(row)
					if slave:
						s_ids = self.create({"slave_id":slave.id, "master_id": row.id, "hashcode": row.hashcode})
						s_ids.update_from_infocoop(row)
						
					else:
						s_ids=s_ids.create_from_infocoop(row)
				else:
					if row.hashcode != s_ids.hashcode:#check hasck
						s_ids.update_from_infocoop(row)
					else:
						pass

		else:
			if row.sync_delete_mark:
				pass
			else:
				slave = self.get_slave_from_row(row)
				if slave:
					s_ids = self.create({"slave_id":slave.id, "master_id": row.id, "hashcode": row.hashcode})
					s_ids.update_from_infocoop(row)
					
				else:
					s_ids=s_ids.create_from_infocoop(row)
		return s_ids


	def get_slave_from_row(self, row):
		'''
		This method must be used to obtain a slave record based on a mirror dbf row
		'''
		raise Exception("This method must be overwrited in implementation")


	def create_from_infocoop(self, row):
		'''When table mirror has a new record do this: Create a new record  master-slave'''
		new = self.env[self.slave_id._name].create((self.prepare_row_fields(row)))
		obj = self.create({"slave_id":new.id, "master_id": row.id, "hashcode": row.hashcode})
		obj.finally_row_fields(row)
		return obj

	def update_from_infocoop(self, row):
		'''When table mirror has a change in a record do this: Send to update process'''
		self.slave_id.write(self.prepare_row_fields(row))
		self.finally_row_fields(row)
		self.hashcode=row.hashcode

	def delete_from_infocoop(self, row):
		'''When table mirror has deleted record, do this: Delete slave record'''
		self.slave_id.unlink()

	def prepare_row_fields(self, row):
		raise Exception("prepare_row_fields funcion must be overwrite")

	def finally_row_fields(self, row):
		return

	def filter(self):
		return []

#	def post_process(self):
#		return
