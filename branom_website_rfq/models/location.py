from odoo import fields, models


class ResCountry(models.Model):
    _inherit = 'res.country'

    restrict_tmpl_id = fields.Many2one('product.sale.restrict')


class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    restrict_tmpl_id = fields.Many2one('product.sale.restrict')
