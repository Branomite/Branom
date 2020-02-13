# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp


class ProductTemplateAttributeValue(models.Model):
    _inherit = 'product.template.attribute.value'

    cost_extra = fields.Float(string='Attribute Extra Cost', default=0.0,
                              digits=dp.get_precision('Product Price'),
                              help='Extra Cost: Extra cost for the variant with this attribute value on sale price. '
                                   'eg. 200 cost extra, 1000 + 200 = 1200.')


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    manufacture_code = fields.Char(string='MC Input')
    position = fields.Integer(string='Position')
    separator = fields.Char(string='Separator')
    affix_type = fields.Selection(string='Prefix/Suffix',
                                  selection=[('prefix', 'Prefix'),
                                             ('suffix', 'Suffix')])


class ProductTemplateAttributeLine(models.Model):
    _inherit = 'product.template.attribute.line'

    # TODO: check with alb for best course of action. We might need a server action. and to handle
    # this in a computed field for the computation of the code
    @api.model_create_multi
    def create(self, vals):
        res = super(ProductTemplateAttributeLine, self).create(vals)
        print("i'm inside create")

        # variant_alone = self.product_tmpl_id._get_valid_product_template_attribute_lines().filtered(
        #     lambda line: line.attribute_id.create_variant == 'always' and len(line.value_ids) == 1).mapped('value_ids')

        # check all lines in the original product template, if they all have only 1, then we need to update the
        # single product's internal reference
        for attr_line in res:
            all_is_one = all(len(line.value_ids) == 1 for line in attr_line.product_tmpl_id.valid_product_template_attribute_line_ids)
            if len(attr_line.product_tmpl_id.product_variant_ids) == 1:
                prod = attr_line.product_tmpl_id.product_variant_id
                prod.default_code = prod.generate_extra_code()
        return res

    @api.multi
    def write(self, vals):
        res = super(ProductTemplateAttributeLine, self).write(vals)
        print("i'm inside the write")
        return res
