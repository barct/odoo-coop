# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
from openerp.osv import osv
from openerp.exceptions import Warning
from openerp.http import request
from openerp.addons.web.controllers.main import content_disposition
from afip_cesp import escribir


class infocoop_tab_fact(models.Model):
    _inherit = "infocoop_tab_fact"

    @api.one
    def download_cesp(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/cesp?period%s' % (self.periodo),
            'target': 'self',
        }
