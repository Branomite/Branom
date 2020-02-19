# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    manufacture_code = fields.Char(string='MC Input')
    position = fields.Integer(string='Position')
    separator = fields.Char(string='Separator')
    affix_type = fields.Selection(string='Prefix/Suffix',
                                  selection=[('prefix', 'Prefix'),
                                             ('suffix', 'Suffix')])

    cost_extra = fields.Float(string='Attribute Extra Cost', default=0.0,
                              digits=dp.get_precision('Product Price'),
                              help='Extra Cost: Extra cost for the variant with this attribute value on sale price. '
                                   'eg. 200 cost extra, 1000 + 200 = 1200.')
