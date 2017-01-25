# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
#from debug import oprint



class Measurements(models.Model):
	_name = "electric_utility.measurement"

	contrat_id = fields.Many2one("electric_utility.contrat", required=True)
	period_id = fields.Many2one('account.period', 'Period', required=True,readonly=True, states={'draft': [('readonly', False)]},)
	last_measure = fields.Integer("Last Measure", required=True)
	last_measure_date = fields.Date("Last Measure Date", required=True)

	current_measure = fields.Integer("Last Measure", required=True)
	current_measure_date = fields.Date("Current Measure Date", required=True)