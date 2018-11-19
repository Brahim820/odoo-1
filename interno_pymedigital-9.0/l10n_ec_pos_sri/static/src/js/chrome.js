odoo.define('l10n_ec_pos_sri.chrome', function (require) {
"use strict";

var PosChrome = require('point_of_sale.chrome');
var core = require('web.core');

var Chrome = PosChrome.Chrome.extend({
    build_chrome: function() {
        var self = this;
        FastClick.attach(document.body);
        core.bus.trigger('set_full_screen', true);

        this.renderElement();

        this.$('.pos-logo').click(function(){
            self.click_logo();
        });

        if(this.pos.config.iface_big_scrollbars){
            this.$el.addClass('big-scrollbars');
        }
    },
    destroy: function() {
        this.pos.destroy();
        core.bus.trigger('set_full_screen', false);
        this._super();
    }
});

return {
    Chrome: Chrome
};
});