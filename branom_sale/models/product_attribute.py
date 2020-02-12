# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp


class ProductTemplateAttributeValue(models.Model):
    _inherit = "product.template.attribute.value"

    cost_extra = fields.Float(
        string="Attribute Cost Extra",
        default=0.0,
        digits=dp.get_precision("Product Price"),
        help="""Cost Extra: Extra cost for the variant with
        this attribute value on sale price. eg. 200 cost extra, 1000 + 200 = 1200.""",
    )
