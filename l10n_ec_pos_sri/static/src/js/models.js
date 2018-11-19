odoo.define('l10n_ec_pos_sri.models', function (require) {
"use strict";

var PosModels = require('point_of_sale.models');
var Backbone = window.Backbone;
var core = require('web.core');
var _t = core._t;

/* Load required fields into res_partner */
PosModels.load_fields("res.partner",['property_account_position_id', 'vat','do_check_vat'])

/* Load required models */
PosModels.load_models([
	{ 
        model:  'account.fiscal.position',
        fields: [],
        loaded: function(self,fiscals){
            self.fiscals = fiscals;
            self.fiscal = null;
            for (var i = 0; i < fiscals.length; i++) {
                self.fiscal = fiscals[i];
            }
        },
    },{
        model:  'res.country.state',
        fields: [],
        loaded: function(self,states){
            self.states = states;
            self.state = null;
            for (var i = 0; i < states.length; i++) {
                self.state = states[i];
            }
        },
    },{
        model:  'product.product',
        fields: ['display_name', 'list_price','price','pos_categ_id', 'taxes_id', 'barcode', 'default_code', 
                 'to_weight', 'uom_id', 'description_sale', 'description',
                 'product_tmpl_id'],
        order:  ['sequence','name'],
        domain: [['sale_ok','=',true],['available_in_pos','=',true]],
        context: function(self){ return { pricelist: self.pricelist.id, display_default_code: false }; },
        loaded: function(self, products){
            self.db.add_products(products);
        },
    },{
        label: 'pictures',
        loaded: function(self){
            self.company_logo = new Image();
            var  logo_loaded = new $.Deferred();
            self.company_logo.onload = function(){
                var img = self.company_logo;
                var ratio = 1;
                var targetwidth = 300;
                var maxheight = 150;
                if( img.width !== targetwidth ){
                    ratio = targetwidth / img.width;
                }
                if( img.height * ratio > maxheight ){
                    ratio = maxheight / img.height;
                }
                var width  = Math.floor(img.width * ratio);
                var height = Math.floor(img.height * ratio);
                var c = document.createElement('canvas');
                    c.width  = width;
                    c.height = height;
                var ctx = c.getContext('2d');
                    ctx.drawImage(self.company_logo,0,0, width, height);

                self.company_logo_base64 = c.toDataURL();
                logo_loaded.resolve();
            };
            self.company_logo.onerror = function(){
                logo_loaded.reject();
            };
                self.company_logo.crossOrigin = "anonymous";
            self.company_logo.src = '/web/binary/company_logo' +'?_'+Math.random();

            return logo_loaded;
        },
    }
])

/* Inherit default function */
PosModels.Orderline.prototype.get_unit_price = function(){
    return this.price;
}
PosModels.Orderline.prototype._compute_all = function(tax, base_amount, quantity) {
    if (tax.amount_type === 'fixed') {
        var ret = tax.amount * quantity;
        return base_amount >= 0 ? ret : ret * -1;
    }
    if ((tax.amount_type === 'percent' && !tax.price_include) || (tax.amount_type === 'division' && tax.price_include)){
        return base_amount * tax.amount / 100;
    }
    if (tax.amount_type === 'percent' && tax.price_include){
        return base_amount - (base_amount / (1 + tax.amount / 100));
    }
    if (tax.amount_type === 'division' && !tax.price_include) {
        return base_amount / (1 - tax.amount / 100) - base_amount;
    }
    return false;
}

PosModels.Paymentline.prototype.get_amount_str = function(){
    return this.amount.toFixed(this.pos.currency.decimals);
}
PosModels.Order.prototype.save_to_db = function(){
    if (!this.init_locked) {
        this.pos.db.save_unpaid_order(this);
    } 
}
PosModels.Order.prototype.init_from_JSON = function(json) {
    var client;
    this.sequence_number = json.sequence_number;
    this.pos.pos_session.sequence_number = Math.max(this.sequence_number+1,this.pos.pos_session.sequence_number);
    this.session_id    = json.pos_session_id;
    this.uid = json.uid;
    this.name = _t("Order ") + this.uid;
    if (json.partner_id) {
        client = this.pos.db.get_partner_by_id(json.partner_id);
        if (!client) {
            console.error('ERROR: trying to load a parner not available in the pos');
        }
    } else {
        client = null;
    }
    this.set_client(client);

    this.temporary = false;     // FIXME
    this.to_invoice = false;    // FIXME

    var orderlines = json.lines;
    for (var i = 0; i < orderlines.length; i++) {
        var orderline = orderlines[i][2];
        this.add_orderline(new PosModels.Orderline({}, {pos: this.pos, order: this, json: orderline}));
    }

    var paymentlines = json.statement_ids;
    for (var i = 0; i < paymentlines.length; i++) {
        var paymentline = paymentlines[i][2];
        var newpaymentline = new PosModels.Paymentline({},{pos: this.pos, order: this, json: paymentline});
        this.paymentlines.add(newpaymentline);

        if (i === paymentlines.length - 1) {
            this.select_paymentline(newpaymentline);
        }
    }
}
PosModels.Order.prototype.export_as_JSON = function() {
    var orderLines, paymentLines;
    orderLines = [];
    this.orderlines.each(_.bind( function(item) {
        return orderLines.push([0, 0, item.export_as_JSON()]);
    }, this));
    paymentLines = [];
    this.paymentlines.each(_.bind( function(item) {
        return paymentLines.push([0, 0, item.export_as_JSON()]);
    }, this));
    return {
        name: this.get_name(),
        amount_paid: this.get_total_paid(),
        amount_total: this.get_total_with_tax(),
        amount_tax: this.get_total_tax(),
        amount_return: this.get_change(),
        lines: orderLines,
        statement_ids: paymentLines,
        pos_session_id: this.pos_session_id,
        partner_id: this.get_client() ? this.get_client().id : false,
        user_id: this.pos.cashier ? this.pos.cashier.id : this.pos.user.id,
        uid: this.uid,
        sequence_number: this.sequence_number,
        creation_date: this.creation_date,
        fiscal_position_id: this.fiscal_position ? this.fiscal_position.id : false
    };
}
PosModels.Order.prototype.export_for_printing = function(){
    var orderlines = [];
    var self = this;

    this.orderlines.each(function(orderline){
        orderlines.push(orderline.export_for_printing());
    });

    var paymentlines = [];
    this.paymentlines.each(function(paymentline){
        paymentlines.push(paymentline.export_for_printing());
    });
    var client  = this.get('client');
    var cashier = this.pos.cashier || this.pos.user;
    var company = this.pos.company;
    var shop    = this.pos.shop;
    var date    = new Date();

    function is_xml(subreceipt){
        return subreceipt ? (subreceipt.split('\n')[0].indexOf('<!DOCTYPE QWEB') >= 0) : false;
    }

    function render_xml(subreceipt){
        if (!is_xml(subreceipt)) {
            return subreceipt;
        } else {
            subreceipt = subreceipt.split('\n').slice(1).join('\n');
            var qweb = new QWeb2.Engine();
                qweb.debug = core.debug;
                qweb.default_dict = _.clone(QWeb.default_dict);
                qweb.add_template('<templates><t t-name="subreceipt">'+subreceipt+'</t></templates>');
            
            return qweb.render('subreceipt',{'pos':self.pos,'widget':self.pos.chrome,'order':self, 'receipt': receipt}) ;
        }
    }

    var receipt = {
        orderlines: orderlines,
        paymentlines: paymentlines,
        subtotal: this.get_subtotal(),
        total_with_tax: this.get_total_with_tax(),
        total_without_tax: this.get_total_without_tax(),
        total_tax: this.get_total_tax(),
        total_paid: this.get_total_paid(),
        total_discount: this.get_total_discount(),
        tax_details: this.get_tax_details(),
        change: this.get_change(),
        name : this.get_name(),
        client: client ? client.name : null ,
        invoice_id: null,   //TODO
        cashier: cashier ? cashier.name : null,
        header: this.pos.config.receipt_header || '',
        footer: this.pos.config.receipt_footer || '',
        precision: {
            price: 2,
            money: 2,
            quantity: 3,
        },
        date: { 
            year: date.getFullYear(), 
            month: date.getMonth(), 
            date: date.getDate(),       // day of the month 
            day: date.getDay(),         // day of the week 
            hour: date.getHours(), 
            minute: date.getMinutes() ,
            isostring: date.toISOString(),
            localestring: date.toLocaleString(),
        }, 
        company:{
            email: company.email,
            website: company.website,
            company_registry: company.company_registry,
            contact_address: company.partner_id[1], 
            vat: company.vat,
            name: company.name,
            phone: company.phone,
            logo:  this.pos.company_logo_base64,
        },
        shop:{
            name: shop.name,
        },
        currency: this.pos.currency,
    };
    
    if (is_xml(this.pos.config.receipt_header)){
        receipt.header_xml = render_xml(this.pos.config.receipt_header);
    }

    if (is_xml(this.pos.config.receipt_footer)){
        receipt.footer_xml = render_xml(this.pos.config.receipt_footer);
    }

    return receipt;
}
});
