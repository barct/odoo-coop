# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
from openerp.osv import osv

class coop_member(models.Model):
    _inherit = "res.partner"

    membership_number = fields.Integer(string='Membership N°', default=None)
    admission_minutes_id = fields.Many2one('minutes','Admission Minutes')
    affiliation_date = fields.Date(string="Affiliation Date")
    disaffiliation_date = fields.Date(string="Disffiliation Date")
    disaffiliation_minutes_id = fields.Many2one('minutes',string='Disaffiliation Minutes')
    reasons_for_disaffiliation = fields.Char(string="Reasons for Disaffiliation ")

    issued_shared_capital = fields.Float(string="Issued Shared Capital")
    subscribed_share_capital = fields.Float(string="Subscribed Shared Capital")
    subscribed_share_capital_cert_number = fields.Integer("Suscribed Share Capital Cert N°")
    subscribed_share_capital_date = fields.Date("Suscribed Share Capital Date")
    is_membership = fields.Boolean(string="Is Membership", compute='get_is_membership', readonly=True)

    def get_is_membership(self):
    	if self.membership_number > 0 and not self.disaffiliation_date:
    		return True
    	return False 

    @api.multi
    def get_next_membership_number(self):
    	self.env.cr.execute("SELECT MAX(membership_number) FROM " + self._table)
    	max = self.env.cr.fetchone()[0] or 0
    	raise osv.except_osv("Information", "Next Membership Number: %s" % (max+1))
    	#self.message_post(subject="Próximo N° Socio: %s" % max+1)

    


    
