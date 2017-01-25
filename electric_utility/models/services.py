# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
#from debug import oprint



class ServiceCategory(models.Model):
	_name = "electric_utility.service_category"

	code = fields.Char("Code", length=7)
	ersep_code = fields.Char("ERSeP Code", length=7)

	name = fields.Char("Name")

	_sql_constraints = [('service_category_unique_keys', 'unique(code)', 'Code must be unique!'),]