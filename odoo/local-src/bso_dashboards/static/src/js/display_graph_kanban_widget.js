odoo.define('bso_dashboard_graph', function (require) {
'use strict';

var kanban_widgets = require('web_kanban.widgets');

var BSODashboardGraph = kanban_widgets.AbstractField.extend({
    start: function() {
        this.graph = JSON.parse(this.field.raw_value);
        this.data = this.graph.data;
        if (this.data){
            this.settings = this.graph.settings;
            this.graph_type = this.settings.type;
            this.display_graph();
        }
        return this._super();
        },


    display_graph : function() {
        var self = this;
        nv.addGraph(function () {
            self.$svg = self.$el.append('<svg>');

            switch(self.graph_type) {

                case "line":
                    self.$svg.addClass('o_graph_linechart');

                    self.chart = nv.models.lineChart()
                        .showLegend(false)
                        //.legendPosition(self.settings.legend_position)
                        .showXAxis(self.settings.show_x_axis)
                        .showYAxis(self.settings.show_y_axis)
                        .rightAlignYAxis(self.settings.right_align_y_axis)
                        .isArea(self.settings.area);
                    self.chart.options({
                        x: function(d, u) { return u },
                        margin: {
                            'left': self.settings.margin_left,
                            'right': self.settings.margin_right,
                            'top': self.settings.margin_top,
                            'bottom': self.settings.margin_bottom
                        },
                    });
                    self.chart.xAxis
                        .tickFormat(function(d) {
                            var label = '';
                            _.each(self.data, function(v, k){
                                if (v.values[d] && v.values[d].x){
                                    label = v.values[d].x;
                                }
                            });
                            return label;
                        });

                    break;

                case "bar":
                    self.$svg.addClass('o_graph_barchart');

                    self.chart = nv.models.discreteBarChart()
                        .showLegend(false)
                        //.legendPosition(self.settings.legend_position)
                        .x(function(d) {
                         return d.label })
                        .y(function(d) {
                        return d.value })
                        .showValues(self.settings.show_values)
                        .showYAxis(self.settings.show_y_axis)
                        .showXAxis(self.settings.show_x_axis)
                        .rightAlignYAxis(self.settings.right_align_y_axis)
                        .staggerLabels(self.settings.stagger_labels)
                        .wrapLabels(self.settings.wrap_labels)
                        .margin({
                            'left': self.settings.margin_left,
                            'right': self.settings.margin_right,
                            'top': self.settings.margin_top,
                            'bottom': self.settings.margin_bottom
                        });
                    self.chart.xAxis.axisLabel(self.data[0].title);
                    self.chart.yAxis.tickFormat(d3.format(',.2f'));

                    break;

                case "pie":
                    self.$svg.addClass('o_graph_piechart');

                    self.chart = nv.models.pieChart()
                        .showLegend(self.settings.show_legend)
                        .legendPosition(self.settings.legend_position)
                        .showLabels(self.settings.show_labels)
                        .labelsOutside(self.settings.labels_outside)
                        .labelType(self.settings.label_type)
                        .donut(self.settings.donut)
                        .labelSunbeamLayout(self.settings.label_sunbeam_layout)
                        .x(function(d) {
                         return d.key })
                        .y(function(d) {
                        return d.value })
                        .margin({
                            'left': self.settings.margin_left,
                            'right': self.settings.margin_right,
                            'top': self.settings.margin_top,
                            'bottom': self.settings.margin_bottom
                        });

                    break;
            }

            var div_kanban_record = self.getParent().$el[0]
            var div_graph_svg = self.$el.find('svg')[0]

            $(div_kanban_record).css({
                'min-width': self.settings.width,
            });
            $(div_graph_svg).css({
                'height': self.settings.height
            });

            d3.select(div_graph_svg)
                .datum(self.data)
                .transition().duration(1200)
                .call(self.chart);

            if (self.settings.show_sum) self.display_sum();
            self.customize_chart();

            nv.utils.windowResize(self.on_resize);
        });
    },

    on_resize: function(){
        this.chart.update();
        this.customize_chart();
    },

    display_sum: function(){
        var self = this;
        var sum = d3.nest()
            .rollup(function(v) { return d3.sum(v, self.chart.y())})
            .entries(self.graph_type == "pie" ? self.data : self.data[0].values);
        var div = this.getParent().$el.find("#sum")[0];
        div.textContent = "Total: " + d3.format(',.2f')(sum);
        div.style.visibility = this.settings.show_sum ? "visible" : "hidden";
    },

    customize_chart: function(){
        if (this.graph_type === 'bar') {
            // Add classes related to time on each bar of the bar chart
            var bar_classes = _.map(this.data[0].values, function (v, k) {return v.type});

            _.each(this.$('.nv-bar'), function(v, k){
                // classList doesn't work with phantomJS & addClass doesn't work with a SVG element
                $(v).attr('class', $(v).attr('class') + ' ' + bar_classes[k]);
            });
        }
    },

    destroy: function(){
        nv.utils.offWindowResize(this.on_resize);
        this._super();
    },
});

kanban_widgets.registry.add('graph', BSODashboardGraph);


});