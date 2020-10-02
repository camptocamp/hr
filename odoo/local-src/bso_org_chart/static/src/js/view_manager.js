odoo.define('get_org_chart.view_manager', function (require) {
    "use strict";
    var ViewManager = require('web.ViewManager');
    var Model = require('web.Model');
    var actionManager = require('web.ActionManager');
    var Widget = require('web.Widget');
    var web_client = require('web.web_client');


    ViewManager.include({

        on_attach_callback: function () {
            var self = this
            self._super();

            self.peopleElement = document.getElementById("people");
            if (self.peopleElement) {
                var parent = self.peopleElement.parentElement
                if (self.peopleElement && parent.classList.contains('org_chart')) {
                    self.peopleElement.style.display = 'block';
                    self.employee_id = self.peopleElement.getAttribute('employee');
                    self.getDatas();
                }
            }
        },

        renderOrgChart: function (data) {
            var chartData = JSON.parse(data);
            var dataSource = chartData.dataSource;

            if (dataSource.length <= 1) {
                this.do_notify('No hierarchy position.');
                return;
            }
            OrgChart.prototype.redirect_node = function (id) {
                var model = new Model('hr.employee');
                return model.call('action_org_chart', [Number(id)]).then(function (action) {
                    web_client.action_manager.do_action(action)
                })
            },

                OrgChart.templates.olivia.field_0 =
                    '<text width="145" style="font-size: 18px;" fill="#757575" x="100" y="35">{val}</text>';
            OrgChart.templates.olivia.field_1 =
                '<text width="145" style="font-size: 14px;" fill="#757575" x="100" y="56">{val}</text>';
            OrgChart.templates.olivia.field_2 =
                '<text width="145" style="font-size: 14px;" fill="#757575" x="100" y="77">{val}</text>';
            OrgChart.templates.olivia.field_3 =
                '<text width="145" style="font-size: 14px;" fill="#757575" x="100" y="98">{val}</text>';

            OrgChart.templates.group.link = '<path stroke-linejoin="round" stroke="#aeaeae" stroke-width="1px" fill="none" d="M{xa},{ya} {xb},{yb} {xc},{yc} L{xd},{yd}" />';
            OrgChart.templates.group.nodeMenuButton = '';
            OrgChart.templates.group.min = Object.assign({}, OrgChart.templates.group);
            OrgChart.templates.group.min.imgs = "{val}";
            OrgChart.templates.group.min.description = '<text width="230" text-overflow="multiline" style="font-size: 14px;" fill="#aeaeae" x="125" y="100" text-anchor="middle">{val}</text>';

            var orgChart = new OrgChart(this.peopleElement, {
                template: "olivia",
                layout: OrgChart.mixed,
                mouseScrool: OrgChart.action.scroll,
                toolbar: {
                    layout: true,
                    zoom: true,
                    fit: true,
                    expandAll: true
                },
                scaleInitial: OrgChart.match.boundary,
                renderNodeEvent: this.renderNodHandler,
                collapse: {
                    level: 3,
                    allChildren: true
                },
                menu: {
                    svg: {text: 'Export SVG'},
                },
                nodeBinding: {
                    field_0: "name",
                    field_1: "title",
                    field_2: "work_location",
                    field_3: "company_id",
                    img_0: "img"
                },

            });
            orgChart.load(dataSource)
            orgChart.on('click', this.redirectNode)
            orgChart.on('expCollClick', this.fitonexpand)

            this.peopleElement.style.display = 'block';

            function preview() {
                OrgChart.pdfPrevUI.show(orgChart, {
                    format: 'A4'
                });
            }
        },
        fitonexpand: function(sender){
            sender.fit()
        },
        getDatas: function () {
            return $.ajax({
                url: '/hr_employee/get_org_chart/' + this.employee_id,
                method: 'GET',
                data: {},
                success: $.proxy(this.renderOrgChart, this),
            });
        },
        redirectNode: function (sender, args) {
            var hash = location.hash;
            var index = hash.indexOf("&");
            var first_hash_attr = hash.substr(1, index - 1);
            if (args.node.id && first_hash_attr.match(/id=*/)) {
                hash = hash.substr(0, 1) +
                    "id=" + args.node.id + hash.substr(index);
                location.hash = hash;
            }
            ;
        }
    });
})