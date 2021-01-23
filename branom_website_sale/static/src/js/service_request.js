odoo.define('branom_website_sale.service_request', function (require) {
'use strict';

console.log('Service Request 13.0.0');

var core = require('web.core');
var publicWidget = require('web.public.widget');

publicWidget.registry.websiteSaleCategory = publicWidget.Widget.extend({
    selector: '#brnm_service_request_form',
    events: {
        'change select[name="country_id"]': '_changeCountry',
    },
    /**
     * @constructor
     */
    init: function () {
        this._super.apply(this, arguments);
        this._changeCountry = _.debounce(this._changeCountry.bind(this), 500);
    },
    /**
     * @override
     */
    start: function () {
        var def = this._super.apply(this, arguments);

        // this._applyHash();

        this.$('select[name="country_id"]').change();

        return def
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {Event} ev
     */
    _changeCountry: function () {
        if (!$("#country_id").val()) {
            return;
        }
        this._rpc({
            route: "/shop/country_infos/" + $("#country_id").val(),
            params: {
                mode: 'shipping',
            },
        }).then(function (data) {
            // populate states and display
            var selectStates = $("select[name='state_id']");
            // dont reload state at first loading (done in qweb)
            if (selectStates.data('init') === 0 || selectStates.find('option').length === 1) {
                if (data.states.length) {
                    selectStates.html('');
                    _.each(data.states, function (x) {
                        var opt = $('<option>').text(x[1])
                            .attr('value', x[0])
                            .attr('data-code', x[2]);
                        selectStates.append(opt);
                    });
                    // selectStates.parent('div').show();
                } else {
                    // selectStates.val('').parent('div').hide();
                }
                selectStates.data('init', 0);
            } else {
                selectStates.data('init', 0);
            }

            // manage fields order / visibility
            // if (data.fields) {
            //     if ($.inArray('zip', data.fields) > $.inArray('city', data.fields)) {
            //         $(".div_zip").before($(".div_city"));
            //     } else {
            //         $(".div_zip").after($(".div_city"));
            //     }
            //     var all_fields = ["street", "zip", "city", "country_name"]; // "state_code"];
            //     _.each(all_fields, function (field) {
            //         $(".checkout_autoformat .div_" + field.split('_')[0]).toggle($.inArray(field, data.fields) >= 0);
            //     });
            // }
        });
    },
});
});
