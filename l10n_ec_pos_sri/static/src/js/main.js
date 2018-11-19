odoo.define('l10n_ec_pos_sri.main', function (require) {
"use strict";

var chrome = require('l10n_ec_pos_sri.chrome');
var core = require('web.core');

core.action_registry.add('pos.ui', chrome.Chrome);

});