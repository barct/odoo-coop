# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields
# , fields, api, _
from suscriber import Suscriber
# from debug import oprint
# import datetime
from openerp.exceptions import Warning

_vars = {}


def global_cache_var(env, var, func):
    '''
    This function implement a cache to avoid repetitive access to the database
    '''
    global _vars
    if var in _vars:
        return _vars[var]
    else:
        _vars[var] = func(env)
        return _vars[var]


class CtaCteInvoice(models.Model, Suscriber):
    _name = "infocoop.cta_cte_invoice"
    master_id = fields.Many2one('infocoop_cta_cte', ondelete='cascade')
    slave_id = fields.Many2one('account.invoice')
    mirror_dependencies = ["infocoop_cta_cte", ]

    def prepare_row_fields(self, row):
        def env_ref(ref):
            '''
            This subfunction is a mask for global_cache_var
            '''
            return global_cache_var(
                env=self.env,
                var=ref,
                func=lambda env: env.ref(ref))

        # calcule account.journal
        # TODO use cache for speed up
        journal_ids = self.env["account.journal"].search([
            ("point_of_sale", "=", int(row.sucursal),)],
            limit=1)
        journal_id = None
        for j in journal_ids:
            for l in j.get_journal_letter():
                if l.name == row.letra:
                    journal_id = j

        if not journal_id:
            raise Warning(
                ("Journal for voucher: %s, and point of sale: %s not found!" %
                    (row.letra, row.sucursal)))

        # get client_id whit cache for efficiency
        contrat = global_cache_var(
            env=self.env,
            var="contrat" + str(row.medidor) + str(row.orden),
            func=lambda env: env["electric_utility.contrat"].search([
                ("contrat_number", "=", str(row.medidor) + str(row.orden)), ],
                limit=1))
        if contrat:
            partner_id = contrat.client_id
            commercial_partner = partner_id.commercial_partner_id
        else:
            raise Exception("Contrat %s%s not found" % (
                row.medidor, row.orden))

        # get document type
        if commercial_partner.afip_responsability_type_id.code == 1:
            document_type_id = env_ref('l10n_ar_account.dc_a_ls')
        else:
            document_type_id = env_ref('l10n_ar_account.dc_b_ls')

        data = {
            "date_invoice": row.fecha,
            "date_due": row.fecha,
            "journal_id": journal_id.id,
            "company_id": self.env.user.company_id.id,
            "currency_id": self.env.user.company_id.currency_id.id,
            # "amount_untaxed": row.neto_serv,
            # "amount_tax": row.neto_imp,
            # "amount_total": row.neto_serv + row.neto_imp,
            "partner_id": partner_id.id,
            "commercial_partner_id": commercial_partner.id,
            "state": "draft",
            "account_id": journal_id.default_debit_account_id.id,
            # "internal_number":  internal_number,
            "sent": False,
            # "period_id": period_id,
            "document_type_id": document_type_id.id,
            # "journal_document_type_id": journal_document_class.id,
            "document_number": row.sucursal + "-" + row.numero,
            "contrat_id": contrat.id,
            "afip_responsability_type_id":
                partner_id.afip_responsability_type_id.id, }
        return data

    def finally_row_fields(self, row):
        pass

    def get_slave_form_row(self, row):
        return self.env["account.payment"].search([
            ("document_number", "=",
                row.num_fact[-12:-8].replace(" ", "0") +
                "-" + row.num_fact[-8:]), ],
            limit=1)

    def filter(self):
        return [("letra", "in", ("A", "B")), ]
