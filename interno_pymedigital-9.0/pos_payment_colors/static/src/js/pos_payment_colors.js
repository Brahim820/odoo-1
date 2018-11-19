odoo.define('pos_payment_colors.pos_payment_colors', function (require) {
"use strict";

	var module = require('point_of_sale.models');
    var models = module.PosModel.prototype.models;

    for(var i=0; i<models.length; i++){
        var model=models[i];

        if(model.model === 'account.journal'){
             model.fields.push('pos_color');
        }
    }

});
