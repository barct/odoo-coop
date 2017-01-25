# -*- coding: utf-8 -*-
import sys
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from dbfread import DBF
#from datetime import date
#from openerp.osv import fields as old_fields

def print_table_structure(table):
	table = DBF(table)
	r=""
	for f in table.fields:
		if f.type=="C":
			r +=  "\n%s = fields.Char(string='%s',length=%s)" % (f.name.lower(), f.name.lower(), f.length)
		elif f.type=="M":
			r += "\n%s = fields.Text(string='%s')" % (f.name.lower(), f.name.lower())
		elif f.type=="N":
			if f.decimal_count>0:
				r += "\n%s = fields.Float(string='%s')" % (f.name.lower(), f.name.lower())
			else:
				r += "\n%s = fields.Integer(string='%s')" % (f.name.lower(), f.name.lower())
		elif f.type=="D":
			r += "\n%s = fields.Date(string='%s')" % (f.name.lower(), f.name.lower())
		elif f.type=="L":
			r += "\n%s = fields.Boolean(string='%s')" % (f.name.lower(), f.name.lower())
		elif f.type=="G":
			r += "\n%s = fields.Binary(string='%s')" % (f.name.lower(), f.name.lower())
		else:
			r += "\n%s" % f	
	print r

print_table_structure(sys.argv[1])