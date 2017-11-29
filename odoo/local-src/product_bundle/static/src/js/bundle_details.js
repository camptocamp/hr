odoo.define('product_bundle.bundle_details', function(require) {
  var action_manager = require('web.ActionManager');
  var ProductBundleActionManager = action_manager.include({
    ir_actions_act_close_wizard_and_reload_view: function (action, options) {
      if (!this.dialog) {
        options.on_close();
      }
      this.dialog_stop();
      this.inner_widget.active_view.controller.reload();
      return $.when();
    },
  });
  return ProductBundleActionManager;
});
