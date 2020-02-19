# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools, _
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp
from odoo.tools.float_utils import float_compare, float_round


class ProductProduct(models.Model):
    _inherit = 'product.product'
    # TODO: remove this field properly.
    cost_extra = fields.Float(
        string='Cost Extra',
        # company_dependent=True,
        digits=dp.get_precision('Product Price'),
        # compute='_compute_product_cost_extra',
        # readonly=True,
        # groups='base.group_user',
        # store=True,
    )

    @api.depends('product_template_attribute_value_ids', 'product_template_attribute_value_ids.cost_extra')
    def _compute_product_cost_extra(self):
        for product in self:
            print(
                f"{product}, {product.product_template_attribute_value_ids}, {product.product_template_attribute_value_ids.cost_extra}"
            )
            product.cost_extra = sum(
                product.mapped('product_template_attribute_value_ids.cost_extra')
            )
    # @api.multi
    # def write(self, values):
    #     ''' Store the standard price change in order to be able to retrieve the cost of a product for a given date'''
    #     res = super(ProductProduct, self).write(values)
    #     print("reach here?!?!")
    #     return res

    @api.multi
    def generate_extra_code(self):
        code = self.product_tmpl_id.base_default_code or ''
        prefix, suffix = '', ''

        for attr_val in self.attribute_value_ids.sorted(key=lambda r: r.position):
            if attr_val.affix_type == 'prefix':
                prefix += attr_val.manufacture_code + attr_val.separator
            elif attr_val.affix_type == 'suffix':
                suffix += attr_val.separator + attr_val.manufacture_code
        return prefix + code + suffix

    @api.model_create_multi
    def create(self, vals_list):
        res = super(ProductProduct, self).create(vals_list)
        for prod in res:
            # Create vendor list for each newly created product
            vendor_ids = prod.product_tmpl_id.variant_seller_ids.mapped('name')

            if len(vendor_ids) == 1:
                vendor_list = self.env['product.supplierinfo'].create([{
                    'name': vendor_ids[0].id,
                    'product_tmpl_id': prod.product_tmpl_id.id,
                    'product_id': prod.id,
                }])
                print(vendor_list)
            else:
                # TODO: add warning popup that pricelist won't be created with 2+ vendors
                print("Placeholder for 0 or 2+ vendors warning")

            # only create code if has attr_values
            if prod.attribute_value_ids:
                prod.default_code = prod.generate_extra_code()
        return res


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    base_standard_price = fields.Float(string='Base Cost', company_dependent=True,
                                       digits=dp.get_precision('Product Price'),
                                       help='Cost used to compute the Vendor Price list with Extra Cost from Variants',
                                       groups='base.group_user', store=True)

    base_default_code = fields.Char(string='Base Internal Reference')

    @api.multi
    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        for tmpl in self.filtered(lambda t: len(t.product_variant_ids) == 1):
            prod = tmpl.product_variant_id
            prod.default_code = prod.generate_extra_code()
        return res


class SupplierInfo(models.Model):
    _inherit = 'product.supplierinfo'

    cost_extra = fields.Float(
        string='Variant Extra Cost',
        # related='product_id.cost_extra',
        compute='_compute_product_cost_extra',
        groups='base.group_user',
        digits=dp.get_precision('Product Price'),
        default=0.0,
        help='The extra cost of this variant based on attribute value\'s cost_extra.',
        store=True,
    )

    price_with_extra = fields.Float(
        string='Price with Extra Cost',
        groups='base.group_user',
        digits=dp.get_precision('Product Price'),
        help='The cost of this variant based on its product variant cost and its attribute values cost_extra.',
        compute='_compute_cost_variant',
        store=True,
    )

    # Compute the cost extra: sum upp the cost_extra for each attribute value on product.product
    # @api.depends('product_id', 'product_id.product_template_attribute_value_ids', 'product_id.product_template_attribute_value_ids.cost_extra')
    @api.depends('product_id', 'product_id.attribute_value_ids')
    def _compute_product_cost_extra(self):
        for vendor_list in self.filtered(lambda v: v.product_id and v.product_id.attribute_value_ids):
            for value in vendor_list.product_id.attribute_value_ids:
                vendor_list.cost_extra += value.cost_extra

    # Compute the total extra cost, includes: product.template's base_standard_price + product.supplierinfo's cost_extra
    @api.depends('product_tmpl_id', 'product_tmpl_id.base_standard_price', 'cost_extra')
    def _compute_cost_variant(self):
        for vendor_list in self.filtered(lambda x: x.product_tmpl_id):
            vendor_list.price_with_extra = vendor_list.product_tmpl_id.base_standard_price + vendor_list.cost_extra
            # Automatically set the price on vendor pricelist
            vendor_list.price = vendor_list.price_with_extra
