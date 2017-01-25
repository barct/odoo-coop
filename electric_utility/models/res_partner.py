# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields

class PartnerContrats(models.Model):
	_inherit = "res.partner"

	contrat_ids = fields.One2many("electric_utility.contrat", "client_id", string="Contrats")