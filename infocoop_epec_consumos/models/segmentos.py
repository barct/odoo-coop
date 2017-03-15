# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
from openerp.osv import osv


class Segmentos(models.Model):

    name = fields.Char()
    code = fields.Char()
    group_id = fields.Many2one("electric_utility.service_category_group", string="Group")
    to = fields.Float("Segment To")


    <field name="group_id" ref="ersep_regulations.service_category_group_ur" />
            <field name="c_from">150</field>
            <field name="c_to">500</field>
            <field name="description">UR2 &gt; 150 y &lt;= 500 kWh mensual</field>