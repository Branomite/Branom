odoo.define('branom_sale.ProductConfiguratorFormRendererBranom', function (require) {
'use strict';

    var ProductConfiguratorFormRenderer = require('sale_product_configurator.ProductConfiguratorFormRenderer');
    var core = require('web.core');
    var _t = core._t;

    console.log('branom_sale.ProductConfiguratorFormRendererBranom v2');

    var ProductConfiguratorFormRendererBranom = ProductConfiguratorFormRenderer.include({
        /**
         * @override
         * Don't actually disable it.
         */
        _disableInput: function ($parent, attributeValueId, excludedBy, attributeNames, productName) {
            var $input = $parent
                .find('option[value=' + attributeValueId + '], input[value=' + attributeValueId + ']');
            $input.addClass('css_not_available');
            $input.closest('label').addClass('css_not_available');
            // $input.prop('disabled', true);

            if (excludedBy && attributeNames) {
                var $target = $input.is('option') ? $input : $input.closest('label').add($input);
                var excludedByData = [];
                if ($target.data('excluded-by')) {
                    excludedByData = JSON.parse($target.data('excluded-by'));
                }

                var excludedByName = attributeNames[excludedBy];
                if (productName) {
                    excludedByName = productName + ' (' + excludedByName + ')';
                }
                excludedByData.push(excludedByName);

                $target.attr('title', _.str.sprintf(_t('Not available with %s'), excludedByData.join(', ')));
                $target.data('excluded-by', JSON.stringify(excludedByData));
            }
        },
    });

    return ProductConfiguratorFormRendererBranom;

});
