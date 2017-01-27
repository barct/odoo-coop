# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api

class Settlement(models.Model):
	_name = "electric_utility.settlement"

	period_id = fields.Many2one("date.range", "Period")
	
	settlement_date = fields.Date("Settlement Date", required=True)
	due_date = fields.Date("Due Date")
	
