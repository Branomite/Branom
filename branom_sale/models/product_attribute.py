from odoo import api, fields, models, _


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute'

    is_show_one = fields.Boolean(string='Show Single Attribute in Configurator',
                                 help='If there is only one attribute value, then show this attribute in product '
                                      'configurator.')


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    manufacture_code = fields.Char(string='MC Input')
    position = fields.Integer(string='Position')
    separator = fields.Char(string='Separator')
    affix_type = fields.Selection(string='Prefix/Suffix',
                                  selection=[('prefix', 'Prefix'),
                                             ('suffix', 'Suffix')])

    cost_extra = fields.Float(string='Attribute Cost Extra', default=0.0,
                              digits='Product Price',
                              help='Cost Extra: Cost Extra for the variant with this attribute value on sale price. '
                                   'eg. 200 cost extra, 1000 + 200 = 1200.')


class ProductTemplateAttributeValue(models.Model):
    _inherit = 'product.template.attribute.value'

    exclude_for = fields.One2many(
        'product.template.attribute.exclusion',
        'product_template_attribute_value_id',
        string="Exclude for",
        relation="product_template_attribute_exclusion",
        help="""Make this attribute value not compatible with
            other values of the product or some attribute values of optional and accessory products.""",
        copy=True)
