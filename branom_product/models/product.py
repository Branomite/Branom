from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_datasheet = fields.Binary('Product Datasheet')
