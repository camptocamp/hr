# -*- coding: utf-8 -*-
import json
import logging

import requests
from resources import User, Issue, Project
from odoo import models, exceptions, _
from requests_oauthlib import OAuth1
from oauthlib.oauth1 import SIGNATURE_RSA

_logger = logging.getLogger(__name__)


class JiraApi(models.TransientModel):
    _name = "jira.api"
    _session = None
    _oauth_session = None

    def _get_oauth_session(self):
        if not self._session:
            self._session = requests.Session()
            settings = self.env['jira.settings'].get()
            oauth = OAuth1(
                settings.consumer_key,
                rsa_key=settings.private_key,
                signature_method=SIGNATURE_RSA,
                resource_owner_key=settings.access_token,
                resource_owner_secret=settings.access_secret
            )
            self._session.verify = settings.verify_ssl
            self._session.auth = oauth

        return self._session

    def _get_session(self):
        if not self._session:
            self._session = requests.Session()
            settings = self.env['jira.settings'].get()
            self._session.auth = (settings.username, settings.api_token)
        return self._session

    def _get(self, endpoint, params=None):
        if not params:
            params = {}
        settings = self.env['jira.settings'].get()
        url_endpoint = '%s%s' % (settings.jira_url, endpoint)
        session = self.env.context.get('session', self._get_oauth_session())
        try:
            resp = session.get(url_endpoint, params=params)
            return resp.status_code, resp.json()
        except Exception as e:
            _logger.error("Cannot Get from Jira API: %s" % e)
            return 0, e

    def _post(self, endpoint, data=None):
        if not data:
            data = {}
        data = json.dumps(data)
        settings = self.env['jira.settings'].get()
        url_endpoint = '%s%s' % (settings.jira_url, endpoint)
        session = self.env.context.get('session', self._get_oauth_session())
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        try:
            resp = session.post(url_endpoint,
                                data=data,
                                headers=headers)
            return resp.status_code, resp.json()
        except Exception as e:
            _logger.error("Cannot Post to Jira API: %s" % e)
            return 0, dict(error="Cannot Post to Jira API: %s" % e)

    def _put(self, endpoint, data=None):
        if not data:
            data = {}
        data = json.dumps(data)
        settings = self.env['jira.settings'].get()
        url_endpoint = '%s%s' % (settings.jira_url, endpoint)
        session = self.env.context.get('session', self._get_oauth_session())
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        resp = session.put(url_endpoint, data=data, headers=headers)
        return resp.status_code

    def _delete(self, endpoint):
        settings = self.env['jira.settings'].get()
        url_endpoint = '%s%s' % (settings.jira_url, endpoint)
        session = self.env.context.get('session', self._get_oauth_session())
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        resp = session.delete(url_endpoint, headers=headers)
        return resp.status_code

    def user(self, email):
        endpoint = '/rest/api/3/user/search'
        params = {
            'query': email
        }
        resp = self._get(endpoint, params)
        if resp[0] == 200:
            if resp[1]:
                return User(resp[1][0]['emailAddress'],
                            resp[1][0]['accountId'])
            raise exceptions.AccessError('User does not exist')
        else:
            raise exceptions.AccessError(_(resp[1]))

    def issue(self, issue_key):
        endpoint = '/rest/api/3/issue/%s' % issue_key
        res = self._get(endpoint)
        if res[0] == 200:
            return Issue(res[1]['key'], res[1]['fields'])

    def create_issue(self, fields):
        endpoint = '/rest/api/3/issue'
        data = {
            'fields': fields
        }
        res = self._post(endpoint, data)
        if res[0] == 201:
            return Issue(res[1]['key'])
        else:
            raise exceptions.AccessError(_(res[1]))

    def project(self, project_key):
        endpoint = '/rest/api/3/project/%s' % project_key
        res = self._get(endpoint)
        if res[0] == 200:
            return Project(
                res[1]['id'],
                res[1]['key'],
                res[1]['name'],
                res[1]['issueTypes'])
        else:
            raise exceptions.AccessError(_(
                'No project could be found with key "%s"' % project_key
            ))

    def search_issues(self, jql_str):
        endpoint = '/rest/api/2/search?jql=%s' % jql_str
        res = self._get(endpoint)
        if res[0] == 200:
            issues = []
            for issue in res[1]['issues']:
                issues.append(Issue(issue['key'], issue['fields']))
            return issues
        else:
            return []

    def assign_issue(self, issue_key, account_id):
        endpoint = '/rest/api/2/issue/%s' % issue_key
        data = {
            'fields': {
                'assignee': {'accountId': account_id},
            }
        }
        status_code = self._put(endpoint, data)
        if status_code == 204:
            return True

    def delete_issue(self, issue_key):
        endpoint = '/rest/api/2/issue/%s' % issue_key
        status_code = self._delete(endpoint)
        if status_code == 204:
            return True
