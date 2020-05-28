# -*- coding: utf-8 -*-
{
    'name': "Branom: Sale Workflow Adjustment for Commission Sales",

    'summary': """
        Branom's development for change in Sale workflow for Sales of the Commission Type.""",

    'description': """
        Task Spec[2009294]:

        1. Prevent the triggering of the procurement process for sales marked as "commission sales"

        2. Bring the customer pricelist functionality to invoices as well

        3. Adjust the unit price on invoice lines automatically
        
        4. Set delivered qty when sale order line is changed after Confirm.
        
        5. Branom wants to set a different income account as the default account listed on invoice lines for commission sales. They would like the option to do so (i.e. in configuration settings).
        
        Task Spec[2118500]:
        
        2.1 Attribute Value Cost Extra Field

        There needs to be a new (Studio) field for “Cost Extra” in the product attribute value model (product.template.attribute.value). This field essentially mirrors the functionality of the “Price Extra” field in that it will be used to calculate additional cost on top of the base product’s cost. The field should be a float and the value is to be configured by the user.
        
        2.2 Vendor Pricelist (New) Price Field
        
        The vendor pricelist model (product.supplierinfo) contains a default “Price” field that simply requires a manually-inputted value. The new price field is a calculated field that pulls the cost (standard_price) of the base product template, the attribute value “cost extra” fields of the attribute values used to configure the new variant, and sums them all together to produce the new vendor pricelist price.
        The new calculated field’s value is then automatically written into the base price field. Now, when the variant is added to an RFQ, the default price will still be pulling from the base vendor pricelist price field, but informed by the new calculated price field.
        
        2.3 Contextual Action for Updating Vendor Pricelist Prices (for products already configured)
        
        There will inevitably be circumstances in which the vendors change the costs of each product and/or attribute value. Therefore, those variants that have already been created, need to have their costs updated to reflect the proper amount. A user would update the cost extra fields of each attribute value, and would run a contextual (server) action to update the vendor pricelist price of each previously created variants.
        
        2.4 Manufacturer Code Auto-Generation
        
        Finally, Branom needs one more value to be generated automatically upon creation of a new variant. Upon creation on a sale order line, a variant must have the “Manufacturer Code” field filled with a generated value to avoid manual entry. The structure of the code is determined by a few custom fields added onto the base product template manufacturer code, which is defined on the attribute value level.
        The first field on the attribute value model is the manufacturer code input value (MC Input). The next field is “Position”. The Position defines how many places from the base manufacture code the MC input value will be set. The third field is “Separator”, which is the symbol or key that comes before/after the MC input value (depending on whether the MC input value is a prefix or a suffix to the base manufacturer code). The final custom field is the “Prefix/Suffix” selection. This determines whether the MC input value comes before or after the base manufacture product code.
    
        Additional Requirements:
        
        1) Would like some standard fields to have the “copied” attribute, so that when you duplicate a product, the following fields are copied over: 
            a. Model: product.template
                i. “Attribute” (attribute_id)
                ii. “Attribute Values” (value_ids)
                iii. “Extra Images” (product_image_ids)
            b. Model: product.template.attribute.value
                i.  “Exclude For” (exclude_for) 
    
        2) Currently, when you add an attribute with a single attribute value to a product, that value will not show up in the product configurator wizard, nor in the variant’s description. Is there a way to enable the ability to have these attributes included in the configurator wizard and variant description? In addition to that, would we be able to add logic to hide some of those attributes (i.e. checkbox)?
    
        NOTE: Hide by default, with the option to Show. Indent each attribute value within the description, display associated MFC prefix before each description of value.
    
        3) Currently, when using the “Exclude For” feature, the values that are excluded are grayed out in the product configurator. Branom would like for these not to appear at all, instead of being grayed out.
            
    """,

    'author': "PS-US Odoo",
    'website': "http://www.odoo.com",
    'category': 'Custom Development',
    'version': '0.1',
    'license': 'OEEL-1',

    # any module necessary for this one to work correctly
    'depends': ['account', 'product', 'sale_account_taxcloud', 'website_sale'],

    # always loaded
    'data': [
        'views/sale_order_views.xml',
        'views/account_invoice_views.xml',
        'views/price_list_views.xml',
        'views/res_config_views.xml',
        'views/product_attribute_views.xml',
        'views/product_views.xml',
        'views/product_template.xml',
        'data/actions.xml',
    ],

}
