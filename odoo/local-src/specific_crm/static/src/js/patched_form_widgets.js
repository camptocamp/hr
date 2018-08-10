// same as the one in web_enterprise, but with no definition of `phone` widget
// actually, it's the same file w/o `phone` widget definition
// - just as if it was never present in here
// https://github.com/odoo/enterprise/blob/f5df970/web_enterprise/static/src/js/views/form_widgets.js
odoo.define('specific_crm.patched_form_widgets', function (require) {
"use strict";

var config = require('web.config');
var core = require('web.core');
var form_widgets = require('web.form_widgets');

var QWeb = core.qweb;

form_widgets.FieldStatus.include({
    template: undefined,
    className: "o_statusbar_status",
    render_value: function() {
        var self = this;
        var $content = $(QWeb.render("FieldStatus.content." + ((config.device.size_class <= config.device.SIZES.XS)? 'mobile' : 'desktop'), {
            'widget': this,
            'value_folded': _.find(this.selection.folded, function (i) {
                return i[0] === self.get('value');
            }),
        }));
        this.$el.empty().append($content.get().reverse());
    },
    bind_stage_click: function () {
        this.$el.on('click','button[data-id]',this.on_click_stage);
    },
});

// XXX: definition of a phone widget has been cut from here, since we don't want
// it to clash w/ a widget defined in `connector-telephony` module

core.form_widget_registry
    // XXX: modified here as well
    .add('upgrade_boolean', form_widgets.FieldBoolean) // community compatibility
    .add('upgrade_radio', form_widgets.FieldRadio); // community compatibility

});
