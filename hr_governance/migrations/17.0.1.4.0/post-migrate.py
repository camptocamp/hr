# Copyright 2025 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from collections import defaultdict

from bs4 import BeautifulSoup
from openupgradelib import openupgrade
from psycopg2.extensions import AsIs

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def fetch_m2m(cr, m2m_tbl, deprecated_table, deprecated_field, related_field):
    """
    Fetch records from m2m table

    :param m2m_tbl: Many2many table name in db
    :param deprecated_table: table name of deprecated class
    :param deprecated_field: field in the deprecated class
    :param related_field: field in the related class
    """
    query = """
        SELECT %(related_field)s, rm_tbl.name
        FROM %(m2m_tbl)s m2m_tbl
        JOIN %(deprecated_table)s rm_tbl ON m2m_tbl.%(deprecated_field)s = rm_tbl.id
            """
    params = {
        "m2m_tbl": AsIs(m2m_tbl),
        "deprecated_table": AsIs(deprecated_table),
        "deprecated_field": AsIs(deprecated_field),
        "related_field": AsIs(related_field),
    }
    openupgrade.logged_query(cr, query, params)
    data = defaultdict(list)
    for res in cr.fetchall():
        data[res[0]].append(res[1])
    return data


def m2m_to_text(data):
    """
    Concatenate list of strings for each record_id

    :param data: result from db
    """
    result = {}
    for key, vals in data.items():
        content = "<ul>" + "".join(f"<li>{val}</li>" for val in vals) + "</ul>"
        result[key] = content
    return result


def migrate(cr, version):  # noqa C901
    env = api.Environment(cr, SUPERUSER_ID, {})
    # Process expectation_ids
    if (
        openupgrade.table_exists(cr, "governance_expectation_governance_role_type_rel")
        and openupgrade.table_exists(cr, "governance_circle_governance_expectation_rel")
        and openupgrade.table_exists(cr, "governance_expectation")
    ):
        _logger.info("Starting to convert expectation_ids to HTML")
        role_expectation_data = fetch_m2m(
            cr,
            "governance_expectation_governance_role_type_rel",
            "governance_expectation",
            "governance_expectation_id",
            "governance_role_type_id",
        )
        processed_role_type = m2m_to_text(role_expectation_data)

        # cache user_input values
        circle_expectation_data = fetch_m2m(
            cr,
            "governance_circle_governance_expectation_rel",
            "governance_expectation",
            "governance_expectation_id",
            "governance_circle_id",
        )
        processed_circle = {}
        for circle_id, texts in circle_expectation_data.items():
            circle = env["governance.circle"].browse(circle_id)
            soup_from_circle = BeautifulSoup(
                "<ul>" + "".join(f"<li>{text}</li>" for text in texts) + "</ul>",
                "html.parser",
            )
            if circle.type_id:
                # extract user_input from value of role
                soup_from_template = BeautifulSoup(
                    processed_role_type.get(circle.type_id.id), "html.parser"
                )
                circle_items = {
                    li.get_text(strip=True) for li in soup_from_circle.find_all("li")
                }
                template_items = {
                    li.get_text(strip=True) for li in soup_from_template.find_all("li")
                }
                user_input = circle_items - template_items
                if user_input:
                    processed_circle[circle.id] = user_input
            else:
                # if it's a circle, preserve everything
                processed_circle[circle.id] = soup_from_circle

        for role_type_id, processed_val in processed_role_type.items():
            role_type = env["governance.role.type"].browse(role_type_id)
            role_type.write({"expectation": processed_val})
        for circle_id, values in processed_circle.items():
            circle = env["governance.circle"].browse(circle_id)
            if circle.type_id:
                # With a role (circle with type), needs to preserve value from template
                # append user_input to final content
                soup_from_template = BeautifulSoup(circle.expectation, "html.parser")
                ul_tag = soup_from_template.find("ul")
                if ul_tag:
                    for item in values:
                        new_li = soup_from_template.new_tag("li")
                        new_li.string = item
                        ul_tag.append(new_li)
                circle.with_context(skip_update_user_input=True).write(
                    {"expectation": ul_tag}
                )
            else:
                circle.with_context(skip_update_user_input=True).write(
                    {"expectation": values}
                )
        _logger.info("Finished converting expectation_ids to text")

    # Process authority_ids
    if (
        openupgrade.table_exists(cr, "governance_authority_governance_role_type_rel")
        and openupgrade.table_exists(cr, "governance_authority_governance_circle_rel")
        and openupgrade.table_exists(cr, "governance_authority")
    ):
        _logger.info("Starting to convert authority_ids to text")
        role_authority_data = fetch_m2m(
            cr,
            "governance_authority_governance_role_type_rel",
            "governance_authority",
            "governance_authority_id",
            "governance_role_type_id",
        )
        processed_role_type = m2m_to_text(role_authority_data)

        # cache user_input values
        circle_authority_data = fetch_m2m(
            cr,
            "governance_authority_governance_circle_rel",
            "governance_authority",
            "governance_authority_id",
            "governance_circle_id",
        )
        processed_circle = {}
        for circle_id, texts in circle_authority_data.items():
            circle = env["governance.circle"].browse(circle_id)
            soup_from_circle = BeautifulSoup(
                "<ul>" + "".join(f"<li>{text}</li>" for text in texts) + "</ul>",
                "html.parser",
            )
            if circle.type_id:
                soup_from_template = BeautifulSoup(
                    processed_role_type.get(circle.type_id.id), "html.parser"
                )
                circle_items = {
                    li.get_text(strip=True) for li in soup_from_circle.find_all("li")
                }
                template_items = {
                    li.get_text(strip=True) for li in soup_from_template.find_all("li")
                }
                user_input = circle_items - template_items
                if user_input:
                    processed_circle[circle.id] = user_input
            else:
                processed_circle[circle.id] = soup_from_circle

        for role_type_id, processed_val in processed_role_type.items():
            role_type = env["governance.role.type"].browse(role_type_id)
            role_type.write({"authority": processed_val})
        # append user_input to final content
        for circle_id, values in processed_circle.items():
            circle = env["governance.circle"].browse(circle_id)
            if circle.type_id:
                soup_from_template = BeautifulSoup(circle.authority, "html.parser")
                ul_tag = soup_from_template.find("ul")
                if ul_tag:
                    for item in values:
                        new_li = soup_from_template.new_tag("li")
                        new_li.string = item
                        ul_tag.append(new_li)
                circle.with_context(skip_update_user_input=True).write(
                    {"authority": ul_tag}
                )
            else:
                circle.with_context(skip_update_user_input=True).write(
                    {"authority": values}
                )

        _logger.info("Finished converting authority_ids to HTML")
