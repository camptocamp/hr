from odoo import fields, models, api, exceptions
from lxml import etree


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def fields_view_get(self, view_id=None, view_type=False, toolbar=False,
                        submenu=False):
        res = super(SaleOrder, self).fields_view_get(view_id=view_id,
                                                     view_type=view_type,
                                                     toolbar=toolbar,
                                                     submenu=submenu)
        if view_type == 'form':
            sale_order_xml = etree.XML(res['arch'])
            order_line_path = "//notebook/page/field[@name='order_line']"
            order_line_field = sale_order_xml.xpath(order_line_path)[0]
            order_line_page = order_line_field.getparent()
            for bundle_id in self.get_bundle_ids():
                bundle_button_xml = self.get_bundle_button_xml(bundle_id)
                order_line_page.insert(0, bundle_button_xml)
            res['arch'] = etree.tostring(sale_order_xml)
        return res

    @api.model
    def get_bundle_ids(self):
        return self.env['product.product'].search([
            ('is_bundle', '=', True)
        ], order='name desc')

    @api.model
    def get_bundle_button_xml(self, bundle_id):
        button_str = """
        <button name="product_bundle.bundle_details_create"
                type="action"
                class="oe_highlight"
                string="Add %s"
                context="{'default_sale_order_id': id, 
                          'default_bundle_id': %s}"/>
        """ % (bundle_id.name, bundle_id.id)
        return etree.XML(button_str)
