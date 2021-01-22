# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

import docusign
import base64
import tempfile
import shutil
import json
import logging
import time

from odoo import api, fields, models
from odoo.exceptions import Warning


_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):

    _inherit = 'sale.order'