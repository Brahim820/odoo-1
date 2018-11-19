odoo.define('default_customer_in_pos', function (require) {
"use strict";

var PosBaseWidget = require('point_of_sale.BaseWidget');
var chrome = require('point_of_sale.chrome');
var gui = require('point_of_sale.gui');
var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var core = require('web.core');
var Model = require('web.DataModel');

var QWeb = core.qweb;
var _t = core._t;

var _super_order = models.Order.prototype;
models.Order = models.Order.extend({

    initialize: function(attributes,options){
	_super_order.initialize.call(this,attributes,options);
        var id_parceiro=this.pos.config.partner_id[0]
	var client = this.pos.db.get_partner_by_id(id_parceiro);
        this.set_client(client);
    },

	
    
});


});
