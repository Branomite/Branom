# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class ProductTemplate(models.Model):
    _inherit = "product.template"

    exclude_discount = fields.Boolean(string='Excluded from Discount', help="When set to true, this product will be excluded from payment term discount on invoice.")

