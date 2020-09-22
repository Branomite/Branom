from odoo import models, fields, api, tools, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def generate_extra_code(self):
        code = self.product_tmpl_id.base_default_code or ''
        prefix, suffix = '', ''

        for attr_val in self.attribute_value_ids.sorted(key=lambda r: r.position):
            separator = attr_val.separator or ''
            separator.replace(' ', '')
            if separator.lower() == 'space':
                separator = ' '
            if attr_val.affix_type == 'prefix':
                prefix += attr_val.manufacture_code + separator
            elif attr_val.affix_type == 'suffix':
                suffix += separator + attr_val.manufacture_code
        return prefix + code + suffix

    @api.model_create_multi
    def create(self, vals_list):
        res = super(ProductProduct, self).create(vals_list)
        for prod in res:
            # Create vendor list for each newly created product
            vendor_ids = prod.product_tmpl_id.variant_seller_ids.mapped('name')

            # Only allow creation of vendor pricelist/product if ONE vendor present per product
            if len(vendor_ids) == 1:
                pricelist = self.env['product.supplierinfo'].create([{
                    'name': vendor_ids[0].id,
                    'product_tmpl_id': prod.product_tmpl_id.id,
                    'product_id': prod.id,
                }])
                # override price and set it to price with extra cost
                pricelist.price = pricelist.price_with_extra

            # only create code if has attr_values
            if prod.attribute_value_ids:
                prod.default_code = prod.generate_extra_code()
        return res


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    base_standard_price = fields.Float(string='Base Cost', company_dependent=True,
                                       digits='Product Price',
                                       default=0.0,
                                       help='Cost used to compute the Vendor Price list with Cost Extra from Variants',
                                       groups='base.group_user', store=True)

    base_default_code = fields.Char(string='Base Manufacturer Product Code',
                                    help='Base Manufacturer Product Code for computing Auto-Generated Manufacturing '
                                         'Code')

    product_image_ids = fields.One2many('product.image', 'product_tmpl_id', string='Images', copy=True)

    attribute_line_ids = fields.One2many('product.template.attribute.line', 'product_tmpl_id',
                                         'Product Attributes', copy=True)

    prod_tmpl_attr_ex_ids = fields.One2many(comodel_name='product.template.attribute.exclusion',
                                            inverse_name='product_tmpl_id',
                                            string='Product Template Attributes Exclusions')

    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        for tmpl in self.filtered(lambda t: len(t.product_variant_ids) == 1):
            prod = tmpl.product_variant_id
            prod.default_code = prod.generate_extra_code()
        return res

    def copy(self, default=None):
        res = super(ProductTemplate, self).copy(default)

        # We need to create new exclusions that map the correct product.template.attribute.values
        # from the original copied prod.tmpl
        ptav = self.env['product.template.attribute.value']
        for prod in res:
            new_ex = []
            for ex in self.prod_tmpl_attr_ex_ids:
                ex_main_attr = ptav.search([('product_tmpl_id', '=', prod.id),
                                            ('product_attribute_value_id', '=',
                                             ex.product_template_attribute_value_id.product_attribute_value_id.id)],
                                           limit=1).id

                ex_values = ptav.search([('product_tmpl_id', '=', prod.id),
                                         ('product_attribute_value_id', 'in',
                                          ex.mapped('value_ids.product_attribute_value_id').ids)]).ids
                cur_ex = {
                    'product_template_attribute_value_id': ex_main_attr,
                    'product_tmpl_id': prod.id,
                    'value_ids': [(6, 0, ex_values)],
                }
                new_ex.append(cur_ex)
            self.env['product.template.attribute.exclusion'].with_context(lang=None).create(new_ex)
        return res


class SupplierInfo(models.Model):
    _inherit = 'product.supplierinfo'

    cost_extra = fields.Float(
        string='Variant Cost Extra',
        compute='_compute_product_cost_extra',
        digits='Product Price',
        default=0.0,
        help='The cost extra of this variant based on attribute value\'s cost_extra.',
        store=True,
    )

    price_with_extra = fields.Float(
        string='Price with Cost Extra',
        digits='Product Price',
        help='The cost of this variant based on its product variant cost and its attribute values cost_extra.',
        compute='_compute_cost_variant',
        default=0.0,
        store=True,
    )

    # Compute the cost extra: sum upp the cost_extra for each attribute value on product.product
    @api.depends('product_id', 'product_id.product_template_attribute_value_ids.product_attribute_value_id.cost_extra')
    def _compute_product_cost_extra(self):
        for vendor_list in self.filtered(lambda v: v.product_id and v.product_id.product_template_attribute_value_ids):
            vendor_list.cost_extra = sum(vendor_list.product_id.product_template_attribute_value_ids.mapped('product_attribute_value_id.cost_extra'))

    # Compute the total cost extra, includes: product.template's base_standard_price + product.supplierinfo's cost_extra
    # @api.depends('product_tmpl_id', 'product_tmpl_id.base_standard_price', 'cost_extra')
    @api.depends('product_tmpl_id', 'cost_extra')
    def _compute_cost_variant(self):
        for vendor_list in self:
            if vendor_list.product_tmpl_id:
                vendor_list.price_with_extra = vendor_list.product_tmpl_id.base_standard_price + vendor_list.cost_extra
                # Automatically set the price on vendor pricelist
                vendor_list.price = vendor_list.price_with_extra
