odoo.define('branom_website_sale.quick_order_popup', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var _t = core._t;

    var timeout;

    publicWidget.registry.websiteQuickOrderLink = publicWidget.Widget.extend({
        selector: '#top_menu a[href$="/quick-order"]',
        events: {
            'mouseenter': '_onMouseEnter',
            'mouseleave': '_onMouseLeave',
        },
        /**
         * @constructor
         */
        // init: function () {
        //     this._super.apply(this, arguments);
        //     //this._popoverRPC = null;
        // },
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
                template: '<div class="popover qc-popover" role="tooltip"><div class="arrow"></div><h3 class="popover-header"></h3><div class="popover-body"></div></div>',
                content: $('#brnm_quick_order_popover').children('form')
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
                if (!self.$el.is(':hover') || $('.qc-popover:visible').length || window.location.pathname == '/quick-order') {
                    return;
                }
                self.$el.popover("show");
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
    });
});