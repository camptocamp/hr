odoo.define('bso_internal_tool.on_card_click', function (require) {
    "use strict";

    var KanbanRecord = require('web_kanban.Record');

    KanbanRecord.include({
        on_card_clicked: function () {
            if (this.model === 'internal.tool') {
                window.open(this.record.url.value);

            } else {
                this._super.apply(this, arguments);
            }
        }
    });
});