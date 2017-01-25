# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)
from debug import oprint



class infocoop_configuration(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = "infocoop_configuration"

    dbf_path = fields.Char(string="Path to dbfs")
    liquidac_invoice_journal_id = fields.Many2one("account.journal", string="Liquidac to Invoice Journal")



    @api.multi
    def get_default_dbf_path(self, fields):
        return {
            'dbf_path': "/var/lib/odoo/virt-env/server/sources/odoo-coop/infocoop/data/dbfs",
        }

    @api.multi
    def get_dbf_path(self):
        return self.env["infocoop_configuration"].search([], limit=1, order="id desc").dbf_path 

    _cache_liquidac_invoice_journal_id = None
    @api.multi
    def get_liquidac_invoice_journal_id(self):
        if  self._cache_liquidac_invoice_journal_id is None:
            #print "leo"
            self._cache_liquidac_invoice_journal_id = self.env["infocoop_configuration"].search([], limit=1, order="id desc").liquidac_invoice_journal_id
        return self._cache_liquidac_invoice_journal_id

    

    @api.multi
    def sync_ingresos(self, *args, **kwargs):
        self.env['infocoop_ingresos'].sync()

    @api.multi
    def sync_tablas(self, *args, **kwargs):
        self.env['infocoop_tablas'].sync()

    @api.multi
    def sync_liquidac(self, *args, **kwargs):
        self.env['infocoop_liquidac'].sync()

    @api.multi
    def sync_auxiliar(self, *args, **kwargs):
        self.env['infocoop_auxiliar'].sync()

    @api.multi
    def sync_ctacte(self, *args, **kwargs):
        self.env['infocoop_ctacte'].sync()

    @api.multi
    def sync_tab_fact(self, *args, **kwargs):
        self.env['infocoop_tab_fact'].sync()

    @api.multi
    def sync_socios(self, *args, **kwargs):
        self.env['infocoop_socios'].sync()

    @api.multi
    def sync_red_usu(self, *args, **kwargs):
        self.env['infocoop_red_usu'].sync()

    @api.multi
    def sync_modi_soc(self, *args, **kwargs):
        self.env['infocoop_modi_soc'].sync()



    @api.multi
    def sync_members(self):
        self.env["infocoop.ingresos_member"].sync_to_odoo()
    
    @api.multi
    def sync_connections(self):
        self.env["infocoop.socios_connection"].sync_to_odoo()

    @api.multi
    def sync_contrats(self):
        self.env["infocoop.socios_contrat"].sync_to_odoo()

    @api.multi
    def sync_settlements(self):
        self.env['infocoop.liquidac_invoice'].sync_to_odoo()