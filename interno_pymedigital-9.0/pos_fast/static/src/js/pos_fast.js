odoo.define('pos_fast', function (require) {

    var models = require('point_of_sale.models');
    var core = require('web.core');
    var _t = core._t;
    var Model = require('web.Model');
    var difference_module = require('pos_product_template.pos_product_template');

    var _superPosModel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        load_server_data: function () {
            var self = this;
            var model_list = []
            var model_datas = []
            var loaded_by_model = {};
            var models = [];
            var models_remove = [];
            var big_model_data = [
                'product.product',
                'res.partner',
            ]
            for (var i = 0; i < this.models.length; i++) {
                var model = this.models[i];
                if (!model['model']) {
                    models.push(model);
                }
                if (model['model'] && big_model_data.indexOf(model['model']) === -1) {
                    models.push(model);
                }
                if (model['model'] && big_model_data.indexOf(model['model']) !== -1) {
                    var tmp = {};
                    model_datas.push({
                        model: model['model'],
                        fields: model['fields'],
                        domain: model['domain'] || [],
                    })
                    loaded_by_model[model['model']] = model['loaded']
                    model_list.push(model['model'])
                    models_remove.push(model)
                }
            }
            this.models = models;
            return _superPosModel.load_server_data.apply(this, arguments).then(function () {
                self.chrome.loading_message(_t('Please waiting some minutes for loading the datas'), 0);
                return new Model('pos.big.data').call('api_get_data', [{
                    model_datas: model_datas
                }]).then(function (datas) {
                    for (var i = 0; i < models_remove.length; i++) {
                        self.models.push(models_remove[i]);
                    }
                    for (var index in model_list) {
                        var object_name = model_list[index];
                        var loaded = loaded_by_model[object_name];
                        if (loaded && datas[object_name]) {
                            if (object_name == 'product.product') {
                                for (var i = 0; i < datas[object_name].length; i++) {
                                    datas[object_name][i]['price'] = datas[object_name][i]['list_price'];
                                }
                            }
                            loaded(self, datas[object_name]);
                        }
                    }
                });
            });
        },

    })
})