odoo.define('pos_sale_pricelist', function (require) {
    var models = require('point_of_sale.models');
    var utils = require('web.utils');
    var round_pr = utils.round_precision;
    var screens = require('point_of_sale.screens');
    var PopupWidget = require("point_of_sale.popups");
    var gui = require('point_of_sale.gui');

    models.load_models([
        {
            model: 'product.pricelist',
            fields: [],
            domain: [],
            loaded: function (self, pricelists) {
                self.pricelist_by_id = {};
                self.pricelist_ids = []
                self.pricelists = pricelists;
                for (var i = 0; i < pricelists.length; i++) {
                    var pricelist = pricelists[i];
                    self.pricelist_by_id[pricelist.id] = pricelist;
                    self.pricelist_ids.push(pricelist.id);
                }
            }
        }, {
            model: 'product.pricelist.item',
            fields: [],
            domain: function (self) {
                return [['pricelist_id', 'in', self.pricelist_ids]]
            },
            loaded: function (self, pricelist_items) {
                self.pricelist_item_ids = [];
                self.pricelist_item_by_id = {};
                self.pricelist_items = pricelist_items;
                self.pricelist_item_by_pricelist_id = {};
                for (var i = 0; i < pricelist_items.length; i++) {
                    var pricelist_item = pricelist_items[i];
                    self.pricelist_item_ids.push(pricelist_item.id);
                    if (!self.pricelist_item_by_pricelist_id[pricelist_item.pricelist_id[0]]) {
                        self.pricelist_item_by_pricelist_id[pricelist_item.pricelist_id[0]] = [pricelist_item];
                    } else {
                        self.pricelist_item_by_pricelist_id[pricelist_item.pricelist_id[0]].push(pricelist_item);
                    }

                }
            }
        }
    ]);


    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        initialize: function (session, attributes) {
            var partner_model = _.find(this.models, function (model) {
                return model.model === 'res.partner';
            });
            partner_model.fields.push('pos_pricelist_id', 'lang');
            var product_model = _.find(this.models, function (model) {
                return model.model === 'product.product';
            });
            product_model.fields.push('standard_price');
            return _super_posmodel.initialize.call(this, session, attributes);
        },
    });
    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        export_as_JSON: function () {
            var json = _super_order.export_as_JSON.apply(this, arguments);
            if (this.pricelist_id) {
                json.pricelist_id = this.pricelist_id;
            }
            return json;
        },
        init_from_JSON: function (json) {
            var res = _super_order.init_from_JSON.apply(this, arguments);
            if (json.pricelist_id) {
                this.pricelist_id = json.pricelist_id;
            }
            return res;
        },
        set_client: function (client) {
            var res = _super_order.set_client.apply(this, arguments);
            if (client && client.pos_pricelist_id && this.orderlines.length) {
                var pricelist_id = client.pos_pricelist_id[0];
                var current_lines = this.orderlines.models
                for (var x = 0; x < current_lines.length; x++) {
                    var line = current_lines[x];
                    var new_price = line.compute_price_rule(pricelist_id);
                    line.set_unit_price(new_price);
                }
                this.pricelist_id = pricelist_id;
                this.trigger('change', this);
            }
            return res;
        },
    });

    models.Orderline = models.Orderline.extend({
        compute_price_rule: function (pricelist_id) {
            var price = this.product.list_price;
            if (pricelist_id) {
                var pricelist_items = this.pos.pricelist_item_by_pricelist_id[pricelist_id];
                var price_tmp = 0;
                var quantity_tmp = 0;
                if (pricelist_items == undefined) {
                    return this.product.list_price;
                }
                for (var i = 0; i < pricelist_items.length; i++) {
                    var pricelist_item = pricelist_items[i];
                    var compute = null;
                    if (this.quantity < pricelist_item.min_quantity) {
                        continue;
                    }
                    if (!pricelist_item.date_start || !pricelist_item.date_end) {
                        compute = true;
                    }
                    if (pricelist_item.date_start && pricelist_item.date_end) {
                        var dt = new Date();
                        var month = dt.getMonth() + 1
                        if (month < 10) {
                            month = '0' + month
                        }
                        var dt_now = dt.getFullYear() + "-" + month + "-" + dt.getDate();
                        if (pricelist_item.date_start <= dt_now && dt_now <= pricelist_item.date_end) {
                            compute = true;
                        }
                    }
                    if (compute == true) {
                        switch (pricelist_item.applied_on) {
                            case 'pos_category':
                                if (this.product.pos_categ_id && this.product.pos_categ_id[0] == pricelist_item.pos_categ_id[0]) {
                                    var compute_price = pricelist_item.compute_price;
                                    if (compute_price == 'fixed') {
                                        price = pricelist_item.fixed_price;
                                    }
                                    if (compute_price == 'percentage') {
                                        price = this.product.list_price - this.product.list_price / 100 * pricelist_item.percent_price
                                    }
                                    if (compute_price == 'formula') {
                                        var base = pricelist_item.base;
                                        if (base == 'list_price') {
                                            price = this.product.list_price;
                                            var price_limit = price;
                                            price = price - price / 100 * pricelist_item.price_discount
                                            if (pricelist_item.price_round) {
                                                price = round_pr(price, pricelist_item.price_round)
                                            }
                                            if (pricelist_item.price_surcharge) {
                                                price += pricelist_item.price_surcharge
                                            }
                                            if (pricelist_item.price_min_margin) {
                                                price = Math.max(price, price_limit + pricelist_item.price_min_margin);
                                            }
                                            if (pricelist_item.price_max_margin) {
                                                price = Math.min(price, price_limit + pricelist_item.price_max_margin);
                                            }
                                        }
                                        if (base == 'standard_price') {
                                            price = this.product.standard_price;
                                            var price_limit = price;
                                            price = this.product.standard_price - this.product.standard_price / 100 * pricelist_item.percent_price
                                            price = price - price / 100 * pricelist_item.price_discount;
                                            price = round_pr(price, pricelist_item.price_round);
                                            price += pricelist_item.price_surcharge;
                                            if (pricelist_item.price_min_margin) {
                                                price = Math.max(price, price_limit + pricelist_item.price_min_margin);
                                            }
                                            if (pricelist_item.price_max_margin) {
                                                price = Math.min(price, price_limit + pricelist_item.price_max_margin);
                                            }
                                        }
                                        if (base == 'pricelist') {
                                            if (pricelist_item.base_pricelist_id) {
                                                price = this.compute_price_rule(pricelist_item.base_pricelist_id[0]);
                                                var price_limit = price;
                                                price = price - price / 100 * pricelist_item.price_discount;
                                                if (pricelist_item.price_round) {
                                                    price = round_pr(price, pricelist_item.price_round);
                                                }
                                                if (pricelist_item.price_surcharge) {
                                                    price += pricelist_item.price_surcharge;
                                                }
                                                if (pricelist_item.price_min_margin) {
                                                    price = Math.max(price, price_limit + pricelist_item.price_min_margin);
                                                }
                                                if (pricelist_item.price_max_margin) {
                                                    price = Math.min(price, price_limit + pricelist_item.price_max_margin);
                                                }
                                            }
                                        }
                                    }
                                }
                            case '1_product':
                                if (this.product.product_tmpl_id && this.product.product_tmpl_id == pricelist_item.product_tmpl_id[0]) {
                                    var compute_price = pricelist_item.compute_price;
                                    if (compute_price == 'fixed') {
                                        price = pricelist_item.fixed_price;
                                    }
                                    if (compute_price == 'percentage') {
                                        price = this.product.list_price - this.product.list_price / 100 * pricelist_item.percent_price
                                    }
                                    if (compute_price == 'formula') {
                                        var base = pricelist_item.base;
                                        if (base == 'list_price') {
                                            price = this.product.list_price;
                                            var price_limit = price;
                                            price = price - price / 100 * pricelist_item.price_discount
                                            if (pricelist_item.price_round) {
                                                price = round_pr(price, pricelist_item.price_round)
                                            }
                                            if (pricelist_item.price_surcharge) {
                                                price += pricelist_item.price_surcharge
                                            }
                                            if (pricelist_item.price_min_margin) {
                                                price = Math.max(price, price_limit + pricelist_item.price_min_margin);
                                            }
                                            if (pricelist_item.price_max_margin) {
                                                price = Math.min(price, price_limit + pricelist_item.price_max_margin);
                                            }
                                        }
                                        if (base == 'standard_price') {
                                            price = this.product.standard_price;
                                            var price_limit = price;
                                            price = this.product.standard_price - this.product.standard_price / 100 * pricelist_item.percent_price
                                            price = price - price / 100 * pricelist_item.price_discount;
                                            price = round_pr(price, pricelist_item.price_round);
                                            price += pricelist_item.price_surcharge;
                                            if (pricelist_item.price_min_margin) {
                                                price = Math.max(price, price_limit + pricelist_item.price_min_margin);
                                            }
                                            if (pricelist_item.price_max_margin) {
                                                price = Math.min(price, price_limit + pricelist_item.price_max_margin);
                                            }
                                        }
                                        if (base == 'pricelist') {
                                            if (pricelist_item.base_pricelist_id) {
                                                price = this.compute_price_rule(pricelist_item.base_pricelist_id[0]);
                                                var price_limit = price;
                                                price = price - price / 100 * pricelist_item.price_discount;
                                                if (pricelist_item.price_round) {
                                                    price = round_pr(price, pricelist_item.price_round);
                                                }
                                                if (pricelist_item.price_surcharge) {
                                                    price += pricelist_item.price_surcharge;
                                                }
                                                if (pricelist_item.price_min_margin) {
                                                    price = Math.max(price, price_limit + pricelist_item.price_min_margin);
                                                }
                                                if (pricelist_item.price_max_margin) {
                                                    price = Math.min(price, price_limit + pricelist_item.price_max_margin);
                                                }
                                            }
                                        }
                                    }
                                }
                            case '0_product_variant':
                                if (this.product.id == pricelist_item.product_id[0]) {
                                    var compute_price = pricelist_item.compute_price;
                                    if (compute_price == 'fixed') {
                                        price = pricelist_item.fixed_price;
                                    }
                                    if (compute_price == 'percentage') {
                                        price = this.product.price - this.product.price / 100 * pricelist_item.percent_price
                                    }
                                    if (compute_price == 'formula') {
                                        var base = pricelist_item.base;
                                        if (base == 'list_price') {
                                            price = this.product.list_price;
                                            var price_limit = price;
                                            price = price - price / 100 * pricelist_item.price_discount
                                            if (pricelist_item.price_round) {
                                                price = round_pr(price, pricelist_item.price_round)
                                            }
                                            if (pricelist_item.price_surcharge) {
                                                price += pricelist_item.price_surcharge
                                            }
                                            if (pricelist_item.price_min_margin) {
                                                price = Math.max(price, price_limit + pricelist_item.price_min_margin);
                                            }
                                            if (pricelist_item.price_max_margin) {
                                                price = Math.min(price, price_limit + pricelist_item.price_max_margin);
                                            }
                                        }
                                        if (base == 'standard_price') {
                                            price = this.product.standard_price;
                                            var price_limit = price;
                                            price = this.product.standard_price - this.product.standard_price / 100 * pricelist_item.percent_price
                                            price = price - price / 100 * pricelist_item.price_discount;
                                            price = round_pr(price, pricelist_item.price_round);
                                            price += pricelist_item.price_surcharge;
                                            if (pricelist_item.price_min_margin) {
                                                price = Math.max(price, price_limit + pricelist_item.price_min_margin);
                                            }
                                            if (pricelist_item.price_max_margin) {
                                                price = Math.min(price, price_limit + pricelist_item.price_max_margin);
                                            }
                                        }
                                        if (base == 'pricelist') {
                                            if (pricelist_item.base_pricelist_id) {
                                                price = this.compute_price_rule(pricelist_item.base_pricelist_id[0]);
                                                var price_limit = price;
                                                price = price - price / 100 * pricelist_item.price_discount;
                                                if (pricelist_item.price_round) {
                                                    price = round_pr(price, pricelist_item.price_round);
                                                }
                                                if (pricelist_item.price_surcharge) {
                                                    price += pricelist_item.price_surcharge;
                                                }
                                                if (pricelist_item.price_min_margin) {
                                                    price = Math.max(price, price_limit + pricelist_item.price_min_margin);
                                                }
                                                if (pricelist_item.price_max_margin) {
                                                    price = Math.min(price, price_limit + pricelist_item.price_max_margin);
                                                }
                                            }
                                        }
                                    }
                                }
                        }
                    }
                    if (this.quantity >= quantity_tmp && this.quantity >= pricelist_item.min_quantity && quantity_tmp <= pricelist_item.min_quantity) {
                        price_tmp = price;
                        quantity_tmp = pricelist_item.min_quantity;
                    }
                    console.log(this.product.display_name + '__' + pricelist_item.id + ' have : ' + price)
                }

            }
            if (price_tmp != price) {
                price = price_tmp;
            }
            var products_ui = $('.product-list >span.product');
            if (products_ui.length) {
                for (var i=0; i < products_ui.length; i ++) {
                    var product_ui = products_ui[i];
                    var product_id = $(product_ui).data('product-id');
                    var product = this.pos.db.get_product_by_id(product_id);
                    if (product && product.id == this.product.id) {
                        $(product_ui).find('.price-tag').attr(
                            'data-original-title', price
                        );
                        $(product_ui).find('.price-tag').attr(
                            'data-toggle', 'tooltip'
                        );
                        $(product_ui).find('.price-tag').tooltip(
                            {delay: {show: 50, hide: 100}}
                        );
                    }
                }
            }
            console.log('set price: ' + price)
            return price;
        },
    });

    var popup_pricelists = PopupWidget.extend({
        template: 'popup_pricelists',
        init: function (parent, options) {
            this._super(parent, options);
        },
        renderElement: function () {
            this.pricelists = this.pos.pricelists;
            this._super();
            var self = this;
            this.pricelist_id = null;
            $('.product').click(function () {
                var pricelist_id = parseInt($(this).data('id'));
                self.pricelist_id = pricelist_id;
                var pricelist = self.pos.pricelist_by_id[pricelist_id];
                if (pricelist) {
                    if ($(this).closest('.product').hasClass("item-selected") == true) {
                        $(this).closest('.product').toggleClass("item-selected");
                    } else {
                        $('.product').removeClass('item-selected');
                        $(this).closest('.product').toggleClass("item-selected");
                    }
                }
                var current_lines = self.pos.get('selectedOrder').orderlines.models;
                if (self.pricelist_id && current_lines.length) {
                    for (var x = 0; x < current_lines.length; x++) {
                        var line = current_lines[x];
                        var new_price = line.compute_price_rule(self.pricelist_id);
                        line.set_unit_price(new_price);
                    }
                }
                if (pricelist_id) {
                    self.pos.get('selectedOrder').pricelist_id = pricelist_id;
                    self.pos.get('selectedOrder').trigger('change', self.pos.get('selectedOrder'));
                }

            });
        }
    })

    gui.define_popup({
        name: 'popup_pricelists',
        widget: popup_pricelists
    });

    var button_pricelist = screens.ActionButtonWidget.extend({
        template: 'button_pricelist',
        button_click: function () {
            this.gui.show_popup('popup_pricelists',{});
        },
    });
    screens.define_action_button({
        'name': 'button_pricelist',
        'widget': button_pricelist,
        'condition': function () {
            return this.pos.config.multi_pricelist == true;
        },
    });

    screens.OrderWidget.include({
        update_summary: function () {
            this._super();
            var order = this.pos.get('selectedOrder');
            var pricelist_id = order.pricelist_id;
            if (this.el.querySelector('.price_list') && pricelist_id) {
                var pricelist = this.pos.pricelist_by_id[pricelist_id];
                this.el.querySelector('.price_list').textContent = pricelist.name;
            }
        }
    })
})
