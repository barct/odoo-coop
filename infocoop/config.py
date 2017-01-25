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

    otra_opcion = fields.Boolean(string="Otra Opción")

    @api.multi
    def get_default_dbf_path(self, fields):
        #print(self.dbf_path)
        #oprint(self.search_read([],"dbf_path"))

        return {
            'dbf_path': "/tmp",
        }

    @api.multi
    def get_dbf_path(self):
        return self.env["infocoop_configuration"].search([], limit=1).dbf_path
     #  return "/var/lib/odoo/virt-env/server/sources/odoo-coop/infocoop/data/dbfs"

    @api.multi
    def sync_ingresos(self, *args, **kwargs):
        self.env['infocoop_ingresos'].sync()

    @api.multi
    def sync_tablas(self, *args, **kwargs):
        self.env['infocoop_tablas'].sync()

    @api.multi
    def sync_members(self):
        #member_suscriptor = env["member_suscriptor"]
        ii_ids = self.env["infocoop_ingresos"].search((["nombre","!=",None],), limit=None, order="socio desc")
        for row in ii_ids:
            s_ids = self.env["infocoop.ingresos_member"].search((["master_id","=",row.id],), limit=1)
            if s_ids:
                #check hasck
                if row.hashcode != s_ids.hashcode:
                    s_ids.update_from_infocoop(row)
                else:
                   pass
            else:
                s_ids.create_from_infocoop(row)
