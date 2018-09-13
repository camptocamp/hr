odoo.define('hr_public_holidays.holidays_highlighter', function (require) {
'use strict';

var calendarView = require('web_calendar.CalendarView');

var Model = require('web.Model');
var hrHolidays = new Model('hr.holidays.public.line');
// tasked w/ fetching desired color from server params
var irConfigParameter = new Model('ir.config_parameter');

calendarView.include({
    get_fc_init_options: function () {
        var res = this._super();

        var oldRenderHandler = res['viewRender'];
        // extend view render callback w/ highlighting functionality
        res['viewRender'] = function (view) {
            oldRenderHandler.apply(this, arguments);  // read as super()
            var visibleDays = $('.o_calendar_view .fc-day');
            var publicHolidays = hrHolidays.call(
                'search_read', [[], ['date']]);
            var holidayColor = irConfigParameter.call(
                'get_param', ['calendar.public_holidays_color']);
            $.when(publicHolidays, visibleDays, holidayColor)
                .then(function (publicHolidays, visibleDays, holidayColor) {
                    // as a result of `search_read` call is the JS object
                    // (dictionary), it's still our duty to clean up results
                    var publicHolidaysArr = publicHolidays.map(x => x['date']);
                    _.each(visibleDays, function (day) {
                        var dayDate = day.getAttribute('data-date');
                        if (publicHolidaysArr.indexOf(dayDate) !== -1) {
                            // found current day in a holiday list, colorize it
                            day.style.backgroundColor = holidayColor;
                        }
                    });
                });
        };

        return res;
    }
});

});
