# -*- coding: utf-8 -*-
import logging
import re

import requests

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class BackboneCympaLink(models.Model):
    _name = 'backbone.cympa.link'
    _rec_name = 'ref'
    _order = "ref ASC"

    _sql_constraints = [
        ('ref_unique', 'UNIQUE (ref)', 'Ref already exists')
    ]

    ref = fields.Char(
        string='Ref',
    )
    a_device_id = fields.Many2one(
        string='Device A',
        comodel_name='backbone.device',
    )
    z_device_id = fields.Many2one(
        string='Device Z',
        comodel_name='backbone.device',
    )
    speed = fields.Integer(
        string='Bearer (Mbps)',
    )
    latency_live = fields.Float(
        string='Latency live (ms)',
        digits=(7, 3),
    )
    link_id = fields.Many2one(
        string='Backbone Link',
        comodel_name='backbone.link',
    )
    status = fields.Boolean(
        string='Status',
    )
    administrative_status = fields.Boolean(
        string='Administrative status',
    )
    operational_status = fields.Boolean(
        string='Operational status',
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    bandwidth_in = fields.Float(
        string='Bandwidth in',
    )
    bandwidth_out = fields.Float(
        string='Bandwidth out',
    )
    destination_ne_latitude = fields.Float(
        digits=(10, 8),
        string='Device Z latitude',
    )
    destination_ne_longitude = fields.Float(
        digits=(11, 8),
        string='Device Z longitude',
    )
    destination_ne_location = fields.Char(
        string='Device Z location',
    )
    entries = fields.Integer(
        string='Entries',
    )
    jitter = fields.Float(
        digits=(9, 5),
        string='Jitter',
    )
    source_ne_latitude = fields.Float(
        digits=(10, 8),
        string='Device A latitude',
    )
    source_ne_longitude = fields.Float(
        digits=(11, 8),
        string='Device A longitude',
    )
    source_ne_location = fields.Char(
        string='Device A location',
    )

    def get_cympa_links(self):
        settings = self.env['backbone.settings'].get()
        cympa_links = self.get_cympa_data(settings)
        if not cympa_links:
            return
        for cympa_ref, cympa_link_dict in cympa_links.iteritems():
            link_dict = self.get_link_data(cympa_ref, cympa_link_dict,
                                           settings)
            backbone_cympa_link = self.search(
                [('ref', '=', cympa_ref),
                 '|', ('active', '=', False), ('active', '=', True)])
            if not backbone_cympa_link:
                self.create(link_dict)
                continue
            backbone_cympa_link.update_backbone_cympa_link(link_dict)
        self.archive_links(cympa_links)
        self.create_links(settings)

    @api.model
    def get_cympa_data(self, settings):
        cympa_api_url = settings.cympa_url
        try:
            r = requests.get(cympa_api_url, auth=(settings.username,
                                                  settings.password))
            return r.json()
        except Exception, e:
            _logger.error("Cannot connect to CYMPA API: %s", e)
            return

    def get_link_data(self, cympa_ref, cympa_link_dict, settings):
        source = cympa_link_dict.get('source_ne')
        destination = cympa_link_dict.get('destination_ne')
        a_device = self.get_device_id(source, settings)
        z_device = self.get_device_id(destination, settings)
        if a_device:
            a_device = a_device.id
        if z_device:
            z_device = z_device.id
        return {
            'ref': cympa_ref,
            'speed': self.convert_cympa_value(cympa_link_dict.get('speed')),
            'latency_live': self.convert_cympa_value(
                cympa_link_dict.get('latency')),
            'a_device_id': a_device,
            'z_device_id': z_device,
            'status': cympa_link_dict.get('status'),
            'administrative_status': cympa_link_dict.get(
                'administrative_status'),
            'operational_status': cympa_link_dict.get(
                'operational_status'),
            'bandwidth_in': self.convert_cympa_value(
                cympa_link_dict.get('bandwidth_in')),
            'bandwidth_out': self.convert_cympa_value(
                cympa_link_dict.get('bandwidth_out')),
            'destination_ne_latitude': cympa_link_dict.get(
                'destination_ne_latitude'),
            'destination_ne_longitude': cympa_link_dict.get(
                'destination_ne_longitude'),
            'destination_ne_location': cympa_link_dict.get(
                'destination_ne_location'),
            'source_ne_latitude': cympa_link_dict.get('source_ne_latitude'),
            'source_ne_longitude': cympa_link_dict.get('source_ne_longitude'),
            'source_ne_location': cympa_link_dict.get(
                'source_ne_location'),
            'entries': cympa_link_dict.get('entries'),
            'jitter': self.convert_cympa_value(
                cympa_link_dict.get('jitter')),
        }

    @api.model
    def convert_cympa_value(self, value):
        # function to rename
        if not value:
            return
        try:
            return float(value) / 1000000
        except ValueError as err:
            _logger.error("ValueError: %s", err)
            return

    def get_device_id(self, device_name, settings):
        if not device_name:
            return
        device_name = device_name.strip()
        device = self.env['backbone.device'].search(
            [('name', '=', device_name)], limit=1)
        if not device and settings.is_creation_enabled:
            return self.create_device(device_name, settings)
        return device

    def create_device(self, device_name, settings):
        if not self.is_device_name_valid(device_name, settings):
            _logger.error("%s does not respect naming convention",
                          device_name)
            return False
        pop_id = self.get_pop_id(device_name, settings)
        return self.env['backbone.device'].create({'name': device_name,
                                                   'pop_id': pop_id})

    @api.model
    def is_device_name_valid(self, device_name, settings):
        return bool(re.findall('^%s-%s-%s$'
                               % (settings.regex_city,
                                  settings.regex_pop,
                                  settings.regex_device), device_name))

    def get_pop_id(self, device_name, settings):
        pop_name = self._extract_pop_name(device_name, settings)
        pop = self.env['backbone.pop'].search([('name', '=', pop_name)])
        if not pop:
            pop = self.env['backbone.pop'].create({'name': pop_name})
        return pop.id

    @api.model
    def _extract_pop_name(self, device_name, settings):
        m = re.search('^%s-%s' % (settings.regex_city, settings.regex_pop),
                      device_name)
        if not m:
            return
        return m.group(0)

    def update_backbone_cympa_link(self, link_dict):
        data = {
            'latency_live': link_dict.get('latency_live'),
        }
        if self.speed != link_dict.get('speed'):
            data['speed'] = link_dict.get('speed')
        if self.status != link_dict.get('status'):
            data['status'] = link_dict.get('status')
        if self.administrative_status != link_dict.get(
                'administrative_status'):
            data['administrative_status'] = link_dict.get(
                'administrative_status')
        if self.operational_status != link_dict.get('operational_status'):
            data['operational_status'] = link_dict.get('operational_status')
        if self.bandwidth_in != link_dict.get('bandwidth_in'):
            data['bandwidth_in'] = link_dict.get('bandwidth_in')
        if self.bandwidth_out != link_dict.get('bandwidth_out'):
            data['bandwidth_out'] = link_dict.get('bandwidth_out')
        if self.destination_ne_latitude != link_dict.get(
                'destination_ne_latitude'):
            data['destination_ne_latitude'] = link_dict.get(
                'destination_ne_latitude')
        if self.destination_ne_longitude != link_dict.get(
                'destination_ne_longitude'):
            data['destination_ne_longitude'] = link_dict.get(
                'destination_ne_longitude')
        if self.destination_ne_location != link_dict.get(
                'destination_ne_location'):
            data['destination_ne_location'] = link_dict.get(
                'destination_ne_location')
        if self.source_ne_latitude != link_dict.get('source_ne_latitude'):
            data['source_ne_latitude'] = link_dict.get('source_ne_latitude')
        if self.source_ne_longitude != link_dict.get('source_ne_longitude'):
            data['source_ne_longitude'] = link_dict.get('source_ne_longitude')
        if self.source_ne_location != link_dict.get('source_ne_location'):
            data['source_ne_location'] = link_dict.get('source_ne_location')
        if self.entries != link_dict.get('entries'):
            data['entries'] = link_dict.get('entries')
        if self.jitter != link_dict.get('jitter'):
            data['jitter'] = link_dict.get('jitter')
        if not self.active:
            data['active'] = True
        if not self.a_device_id:
            data['a_device_id'] = link_dict.get('a_device_id')
        if not self.z_device_id:
            data['z_device_id'] = link_dict.get('z_device_id')
        self.write(data)

    def archive_links(self, cympa_links):
        disabled_links = self.search(
            [('ref', 'not in', cympa_links.keys())])
        disabled_links.write({'active': False})

    def create_links(self, settings):
        cympa_links = self.get_cympa_links_to_match()
        for cympa_link in cympa_links:
            backbone_links = cympa_link.get_corresponding_backbone_links()
            if not backbone_links and settings.is_creation_enabled:
                self.env['backbone.link'].create(
                    {'a_device_id': cympa_link.a_device_id.id,
                     'z_device_id': cympa_link.z_device_id.id,
                     'cympa_id': cympa_link.id})
            elif len(backbone_links) == 1:
                backbone_links.write({'cympa_id': cympa_link.id})

    def get_cympa_links_to_match(self):
        return self.search([
            ('link_id', '=', False),
            ('a_device_id', '!=', False),
            ('z_device_id', '!=', False)
        ])

    def get_corresponding_backbone_links(self):
        return self.env['backbone.link'].search([
            ('a_device_id', 'in',
             (self.a_device_id.id, self.z_device_id.id)),
            ('z_device_id', 'in',
             (self.a_device_id.id, self.z_device_id.id)),
            ('cympa_id', '=', False),
        ])

    @api.multi
    def write(self, values):
        settings = self.env['backbone.settings'].get()
        record = super(BackboneCympaLink, self).write(values)
        for rec in self:
            if 'link_id' in values:
                rec.break_link(values['link_id'])
            if not rec.link_id:
                continue
            data = {
                'latency_live': rec.latency_live,
            }
            if rec.id != rec.link_id.cympa_id.id:
                data['cympa_id'] = rec.id
            if rec.speed != rec.link_id.bearer:
                data['bearer'] = rec.speed
            if settings.is_archiving_enabled and 'active' in values:
                data['active'] = values['active']
            rec.link_id.write(data)
        return record

    def break_link(self, exclude_link_id):
        self.link_id.search([
            ('cympa_id', '=', self.id),
            ('id', '!=', exclude_link_id)
        ]).write({'cympa_id': False})
