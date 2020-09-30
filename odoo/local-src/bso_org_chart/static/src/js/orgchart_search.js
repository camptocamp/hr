OrgChart.searchUI.prototype._serverSearch = function (t) {
    var parse_data = function (data) {
        data = JSON.parse(data);
        data = data.dataSource;
        get_search_hint(this, data)
    }

    $.ajax({
        url: '/hr_employee/name/' + t,
        method: 'GET',
        data: {},
        success: $.proxy(parse_data, this)
    });

    var get_search_hint = function (self, nodes) {
        for (
            var e = self,
                r = self.obj.element.querySelector('[data-id="container"]'),
                i = self.obj.element.querySelector('[data-id="search"]'),
                a = nodes,
                n = "",
                o = 0;
            o < a.length;
            o++) {
            var l = a[o],
                s = "";
            l.img && (s = '<img style="padding: 2px 0px  2px 7px;width:32px;height:32px;" src="' + l.img + '" / >'), n += OrgChart.searchUI.createItem(s, l)
        }
        r.innerHTML = n;
        var h = i.querySelectorAll("[data-search-item-id]");
        for (o = 0; o < h.length; o++) h[o].addEventListener("click", function () {
            var t = OrgChart.events.publish("searchclick", [e.obj, this.getAttribute("data-search-item-id")]);
            null != t && 1 != t || e.obj.redirect_node(this.getAttribute("data-search-item-id"))
        }), h[o].addEventListener("mouseover", function () {
            this.setAttribute("data-selected", "yes"), this.style.backgroundColor = "#f0f0f0"
        }), h[o].addEventListener("mouseleave", function () {
            this.style.backgroundColor = "inherit", this.setAttribute("data-selected", "no")
        })
    }
}
