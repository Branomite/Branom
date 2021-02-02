odoo.define('branom_website_sale.quick_order_popup', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var brnm_quick_order = require('branom_website_sale.quick_order');
    var core = require('web.core');
    var _t = core._t;

    var timeout;

    publicWidget.registry.websiteQuickOrderLink = publicWidget.Widget.extend({
        selector: '#top_menu a[href$="/quick-order"]',
        events: {
            'mouseenter': '_onMouseEnter',
            'mouseleave': '_onMouseLeave',
            'click': '_onClick',
        },
        /**
         * @constructor
         */
        init: function () {
            this._super.apply(this, arguments);
            this._popoverRPC = null;
        },
        /**
         * @override
         */
        start: function () {
            this.$el.popover({
                trigger: 'manual',
                animation: true,
                html: true,
                title: function () {
                    return _t("Quick Order");
                },
                container: 'body',
                placement: 'auto',
                sanitize: false,
                template: '<div class="popover qc-popover" role="tooltip"><div class="arrow"></div><h3 class="popover-header"></h3><div class="popover-body"></div></div>'
            });
            return this._super.apply(this, arguments);
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * @private
         * @param {Event} ev
         */
        _onMouseEnter: function (ev) {
            var self = this;
            clearTimeout(timeout);
            $(this.selector).not(ev.currentTarget).popover('hide');
            timeout = setTimeout(function () {
                console.log(window.location.pathname);
                if (!self.$el.is(':hover') || $('.qc-popover:visible').length || window.location.pathname == '/quick-order') {
                    return;
                }
                self._popoverRPC = $.get("/quick-order", {
                    type: 'popover',
                }).then(function (data) {
                    self.$el.data("bs.popover").config.content = data;
                    self.$el.popover("show");
                    // enable popover form validation
                    $('input.brnm_sku_input').each(function (index, sku_input) {
                        brnm_quick_order.bindSKUValidation(sku_input);
                    });
                    $('#brnm_qo_add_item').on('click', brnm_quick_order.addRowCallback);
                    $('#brnm_quickorder_form').on('submit', brnm_quick_order.formSubmitCallback);
                    $('.popover').on('mouseleave', function () {
                        self.$el.trigger('mouseleave');
                    });
                });
            }, 300);
        },
        /**
         * @private
         * @param {Event} ev
         */
        _onMouseLeave: function (ev) {
            var self = this;
            setTimeout(function () {
                if ($('.popover:hover').length) {
                    return;
                }
                if (!self.$el.is(':hover')) {
                    self.$el.popover('hide');
                }
            }, 1000);
        },
        /**
         * @private
         * @param {Event} ev
         */
        _onClick: function (ev) {
            // When clicking on the cart link, prevent any popover to show up (by
            // clearing the related setTimeout) and, if a popover rpc is ongoing,
            // wait for it to be completed before going to the link's href. Indeed,
            // going to that page may perform the same computation the popover rpc
            // is already doing.
            clearTimeout(timeout);
            if (this._popoverRPC && this._popoverRPC.state() === 'pending') {
                ev.preventDefault();
                var href = ev.currentTarget.href;
                this._popoverRPC.then(function () {
                    window.location.href = href;
                });
            }
        },
    });
});