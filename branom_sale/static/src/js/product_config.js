odoo.define('branom_sale.ProductConfiguratorFormRendererBranom', function (require) {
'use strict';

var ProductConfiguratorFormRenderer = require('sale.ProductConfiguratorFormRenderer');

var ProductConfiguratorFormRendererBranom = ProductConfiguratorFormRenderer.include({
    /**
     * @override
     */

    _checkExclusions: function ($parent, combination) {
        this._super.apply(this, arguments);
        function hide_excluded_products($parent) {
            function setOriginalSelect ($select) {
                if ($select.data("originalHTML") == undefined) {
                    $select.find('option').each( function() {
                        $(this).removeAttr('class');
                        $(this).removeAttr('selected');
                    }
                    );
                    $select.data("originalHTML", $select.html());
                } // Only reset if empty
            }

            function restoreOptions ($select, cur_selected) {
                var ogHTML = $select.data("originalHTML");
                if (ogHTML != undefined) {
                    $select.html(ogHTML);
                }
                $select.find('option').each( function() {
                        if ($(this).val() == cur_selected) {
                            $(this).attr("selected","selected");
                        }
                    });
            }

            var product_exclusions = $parent.find('ul[data-attribute_exclusions]').data('attribute_exclusions').exclusions
            // Grab the values that are currently selected
            var values = [];
            var variantsValuesSelectors = [
                'input.js_variant_change:checked',
                'select.js_variant_change'
            ];
            _.each($parent.find(variantsValuesSelectors.join(', ')), function (el) {
                values.push(+$(el).val());
                $(el).each(function(){
                    setOriginalSelect($(this));
                    restoreOptions($(this), +$(el).val());
                });
            });
            //Handle radio button with hide/show
            $('input').parent().parent().show();
            for (var val of values) {
                var hide = product_exclusions[val]
                for (var h of hide) {
                    $('option[value="'+ h +'"]').remove();
                    $('input[value="'+ h +'"]').parent().parent().hide();
                }
            }
        } // End hide_excluded_products
        hide_excluded_products($parent);
    },
});

return ProductConfiguratorFormRendererBranom;

});
