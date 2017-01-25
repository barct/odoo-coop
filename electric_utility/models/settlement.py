# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api

class Settlement(models.Model):
	_name = "electric_utility.settlement"

	period_id = fields.Many2one("account.period", "Period")
	settlement_date = fields.Date("Settlement Date")
	due_date = fields.Date("Due Date")
	
