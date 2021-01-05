from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    rfq_enabled = fields.Boolean('RFQ Product')
    restrict_sale_loc_tmpl = fields.Many2one('product.sale.restrict', string='Template')

    # Ensure the assigned template is removed if boolean is unchecked
    @api.onchange('rfq_enabled')
    def _update_rfq_tmpl(self):
        if not self.rfq_enabled:
            self.restrict_sale_loc_tmpl = False

    @api.model
    def is_rfq_product(self, partner):
        # False - Restrict sale to RFQ
        # True - Allow Sale on Website

        if self.rfq_enabled and not self.restrict_sale_loc_tmpl:
            return False

        # Check partner to see if sale is allowed
        if partner and self.restrict_sale_loc_tmpl:
            if partner.country_id in self.restrict_sale_loc_tmpl.mapped('country_ids'):
                return True

            if partner.state_id in self.restrict_sale_loc_tmpl.mapped('state_ids'):
                return True

            if int(self.restrict_sale_loc_tmpl.zip_from) <= int(partner.zip) <= int(self.restrict_sale_loc_tmpl.zip_to):
                return True
        else:
            return False


class ProductProduct(models.Model):
    _inherit = 'product.product'

    rfq_enabled = fields.Boolean(related='product_tmpl_id.rfq_enabled', string='RFQ Product')
    order_id = fields.Many2one('sale.order', string='Sale Order')

    def is_rfq_enabled(self, *partner_id):
        if partner_id:
            for product in self:
                product.product_tmpl_id.is_rfq_enabled(partner_id)
        else:
            return False


class ProductSaleRestrict(models.Model):
    _name = 'product.sale.restrict'

    name = fields.Char('Template Name')
    country_ids = fields.Many2many(comodel_name='res.country', string='Allow sales for Countries')
    state_ids = fields.Many2many(comodel_name='res.country.state', string='Allow sales for States')
    zip_from = fields.Char('Zip From')
    zip_to = fields.Char('Zip To')
