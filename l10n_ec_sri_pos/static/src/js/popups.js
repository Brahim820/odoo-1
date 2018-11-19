odoo.define('l10n_ec_pos_sri.popups', function (require) {
    "use strict";

    var PopupWidget = require('point_of_sale.popups');
    var gui = require('point_of_sale.gui');

    var SRIPosSelectionPopupWidget = PopupWidget.extend({
        template: 'SRIPosSelectionPopupWidget',
        init: function(parent, args) {
            this._super(parent, args);
            this.options = {};
        },
        show: function(options){
            options = options || {};
            var self = this;
            this._super(options);

            this.list    = options.list    || [];
            this.renderElement();
        },
        click_item : function(event) {
            this.gui.close_popup();
            if (this.options.confirm) {
                var item = this.list[parseInt($(event.target).data('item-index'))];
                item = item ? item.item : item;
                this.options.confirm.call(self,item);
            } else {

            }
        }
    });
    gui.define_popup({name:'sri_pos_selection', widget: SRIPosSelectionPopupWidget});

    return SRIPosSelectionPopupWidget;
});