odoo.define('l10n_ec_pos_sri.db', function (require) {
"use strict";

var PosDB = require('point_of_sale.DB');
var PosDB = PosDB.include({

    _partner_search_string: function(partner){
        var str =  partner.name;
        if(partner.barcode){
            str += '|' + partner.barcode;
        }
        if(partner.address){
            str += '|' + partner.address;
        }
        if(partner.vat){
            str += '|' + partner.vat;
        }
        if(partner.phone){
            str += '|' + partner.phone.split(' ').join('');
        }
        if(partner.mobile){
            str += '|' + partner.mobile.split(' ').join('');
        }
        if(partner.email){
            str += '|' + partner.email;
        }
        str = '' + partner.id + ':' + str.replace(':','') + '\n';
        return str;
    },
    });
});
