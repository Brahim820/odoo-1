odoo.define('pos_multi_receipt.pos_multi_receipt', function(require){
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var Model = require('web.DataModel');
    var gui = require('point_of_sale.gui');
    var models = require('point_of_sale.models');
    var QWeb = core.qweb;

    screens.ReceiptScreenWidget.extend({
        print_xml: function() {
            var env = {
                widget:  this,
                receipt: this.pos.get_order().export_for_printing(),
                paymentlines: this.pos.get_order().get_paymentlines()
            };
            var receipt = QWeb.render('XmlReceipt',env);

            var count = this.pos.config.multi_receipt_count;
            for(var i=0;i<count;i++){
                this.pos.proxy.print_receipt(receipt);
            }
            this.pos.get_order()._printed = true;
        },
    });
});
