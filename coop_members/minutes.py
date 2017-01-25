# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
#from datetime import date
#from openerp.osv import fields as old_fields


class minutes(models.Model):
	
	def get_last_minutes(self, field):
		minutes = self.search([])
		if len(minutes)>0:
			last_minutes = max(self.search([]), key=lambda o: (o.book_number,o.number))
			return getattr(last_minutes, field)
		else:
			return 0
		

	book_number = fields.Integer(string='Book N°', default=lambda o: o.get_last_minutes('book_number'))
	number = fields.Integer(string='Minutes N°', default=lambda o: o.get_last_minutes('number')+1)
	date = fields.Date(string='Date')

	@api.multi
	def name_get(self):
		super(minutes, self).name_get()
		data = []
		for minute in self:
			data.append((minute.id,"Libro: %s - Acta: %s" % (minute.book_number,minute.number)))
		return  data


	@api.multi
	def last_book(self):
		for i in self:
			print i
		return max(self).book_number

	
