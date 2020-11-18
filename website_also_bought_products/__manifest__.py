# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Website Also Bought Products",
  "summary"              :  """Odoo Website Also Bought Products Module lets you implement ‘people who bought this item also bought’ strategy on your website.""",
  "category"             :  "Website",
  "version"              :  "1.0.1",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=website_also_bought_products",
  "depends"              :  [
                             'website_sale_delivery',
                             'website_webkul_addons',
                            ],
  "data"                 :  [
                             'views/product_view.xml',
                             'views/res_conf_view.xml',
                             'views/webkul_addons_config_inherit_view.xml',
                             'views/template.xml',
                            ],
  "demo"                 :  ['data/demo.xml'],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  59,
  "currency"             :  "USD",
}