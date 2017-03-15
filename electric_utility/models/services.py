# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api


class ServiceCategoryGroup(models.Model):
    _name = "electric_utility.service_category_group"
    code = fields.Char("Code", length=7)
    name = fields.Char("Name")
    segments = fields.Char("Segments")

    def define_segment(self, value):
        level = 1
        if self.segments:
            segs = self.segments.split(",")
            s = None
            for s in segs:
                if value <= float(s):
                    break
                level += 1
        return self.code, level

    def get_segments(self):
        self.ensure_one()


class ServiceCategory(models.Model):
    _name = "electric_utility.service_category"

    code = fields.Char("Code", length=7)
    ersep_code = fields.Char("ERSeP Code", length=7)
    group_id = fields.Many2one("electric_utility.service_category_group")
    name = fields.Char("Name")

    _sql_constraints = [('service_category_unique_keys',
                         'unique(code)', 'Code must be unique!'), ]
