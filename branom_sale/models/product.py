# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools, _
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp
from odoo.tools.float_utils import float_compare, float_round


class ProductProduct(models.Model):
    _inherit = "product.product"

    cost_extra = fields.Float(
        string="Cost Extra",
        company_dependent=True,
        digits=dp.get_precision("Product Price"),
        compute="_compute_product_cost_extra",
        readonly=True,
        groups="base.group_user",
        store=True,
    )

    @api.depends("product_template_attribute_value_ids", "product_template_attribute_value_ids.cost_extra")
    def _compute_product_cost_extra(self):
        for product in self:
            print(
                f"{product}, {product.product_template_attribute_value_ids}, {product.product_template_attribute_value_ids.cost_extra}"
            )
            product.cost_extra = sum(
                product.mapped("product_template_attribute_value_ids.cost_extra")
            )


class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    cost_extra = fields.Float(
        string="Variant Cost Extra",
        # related="product_id.cost_extra",
        compute="_compute_product_cost_extra",
        groups="base.group_user",
        digits=dp.get_precision("Product Price"),
        default=0.0,
        help="The extra cost of this variant based on attribute value's cost_extra.",
    )

    price_with_extra = fields.Float(
        string="Price with Extra Cost",
        groups="base.group_user",
        digits=dp.get_precision("Product Price"),
        help="The cost of this variant based on its product variant cost and its attribute values' cost_extra.",
        compute="_compute_cost_variant",
        store=True,
    )

    @api.depends('product_id', 'product_id.product_template_attribute_value_ids', 'product_id.product_template_attribute_value_ids.cost_extra')
    def _compute_product_cost_extra(self):
        for vendor_list in self.filtered(lambda v: v.product_id and v.product_id.product_template_attribute_value_ids):
            # vendor_list.cost_extra = vendor_list.product_id.cost_extra

            # vendor_list.cost_extra = sum(
            #     vendor_list.product_id.mapped("product_template_attribute_value_ids.cost_extra")
            # )
            # for cost in vendor_list.product_id.product_template_attribute_value_ids.mapped('cost_extra'):
            for value in vendor_list.product_id.product_template_attribute_value_ids:
                vendor_list.cost_extra += value.cost_extra

    @api.depends('product_id', 'product_id.standard_price', 'cost_extra')
    def _compute_cost_variant(self):
        for vendor_list in self.filtered(lambda x: x.product_id):
            # TODO: check if they want to use old Price in this configuration or just computed
            vendor_list.price_with_extra = vendor_list.product_id.standard_price + vendor_list.cost_extra
            # if cost:
            #     self.price_with_extra = cost
            # else:
            #     for rec in self:
            #         rec.price = rec.price_variant

            # set Odoo price field to the new calculated field that has extra cost + list price
            vendor_list.price = vendor_list.price_with_extra
        # TODO: check what to pass into this func below
    #     self._set_cost_variant(1)
    #
    # def _set_cost_variant(self, cost):
    #     if cost:
    #         self.price_variant = cost
    #     else:
    #         for rec in self:
    #             rec.price = rec.price_variant
