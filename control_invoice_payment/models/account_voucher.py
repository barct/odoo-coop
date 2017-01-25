# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)


class account_voucher(models.Model):

	_inherit = "account.voucher"

	@api.multi
	def proforma_voucher(self):
		ret = super(account_voucher, self).proforma_voucher()
		print "Aveztruz----"
		
		for voucher in self:
			if voucher.journal_id.type in ("bank","cash"):
				abs_id = self.env["account.bank.statement"].search([("journal_id","=",voucher.journal_id.id),("state","=","open")],limit=1).id
				if not abs_id:
					raise Warning(
						_('Cash control for the journal %s is not open!' % (voucher.journal_id.name))
						)
					
				for v_line in voucher.line_ids:
					statement_line_vals={
						'statement_id': abs_id,
						'amount': v_line.amount,
						'date': voucher.date,
						'name': voucher.document_number,
						'partner_id': voucher.partner_id.id,
						'account_id': v_line.account_id.id,
						}
					#print statement_line_vals
					self.env['account.bank.statement.line'].create(statement_line_vals)
			#raise Warning("TODO OK")
		return ret

