from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    manufacturer_id = fields.Many2one('res.partner', string='Manufacturer',
                                      domain="[('is_company', '=', True)]")
