odoo.define('branom_website_sale.service_request', function (require) {
'use strict';

// console.log('Service Request 13.0.3');

var core = require('web.core');
var publicWidget = require('web.public.widget');

publicWidget.registry.websiteSaleCategory = publicWidget.Widget.extend({
    selector: '#brnm_service_request_form',
    events: {
        'change select[name="country_id"]': '_changeCountry',
        'change input[name="payment"]': '_changePayment',
        'change input[name="return"]': '_changeReturn',
        'change input[name="return_info"]': '_changeReturnInfo',
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
                    selectStates.val('');
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
    _changePayment: function (ev) {
        var val = $('input[name="payment"]:checked').val();
        var $po_input = $('input[name="po"]');
        if (val === "Purchase Order") {
            $po_input.prop('required', true);
            $po_input.prop('disabled', false);
        } else {
            $po_input.prop('required', false);
            $po_input.prop('disabled', true);
        }
    },
    _changeReturn: function (ev) {
        var val = $('input[name="return"]:checked').val();
        var $return_info = $('input[name="return_info"]');
        if (val === "Pick Up") {
            $return_info.prop('required', false);
            $return_info.prop('disabled', true);
        } else {
            $return_info.prop('required', true);
            $return_info.prop('disabled', false);
        }
    },
    _changeReturnInfo: function (ev) {
        var val = $('input[name="return_info"]:checked').val();
        var $collect_num = $('input[name="collect_num"]');
        if (val === "Collect") {
            $collect_num.prop('required', true);
            $collect_num.prop('disabled', false);
        } else {
            $collect_num.prop('required', false);
            $collect_num.prop('disabled', true);
        }
    },
});
});
