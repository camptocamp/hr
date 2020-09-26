# -*- coding: utf-8 -*-
import json

import werkzeug


def _response(res):
    headers = {'Content-Type': 'application/json'}
    return werkzeug.wrappers.Response(
        json.dumps(res), status=200, headers=headers)
