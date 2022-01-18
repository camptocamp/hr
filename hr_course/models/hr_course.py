# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import api, fields, models


class HRCourseAttendee(models.Model):
    _name = "hr.course.attendee"
    _description = "Course Attendee"

    course_schedule_id = fields.Many2one(
        "hr.course.schedule", ondelete="cascade", readonly=True, required=True
    )
    course_id = fields.Many2one(related="course_schedule_id.course_id")
    course_validity_end_date = fields.Date(related="course_id.validity_end_date")

    name = fields.Char(related="course_schedule_id.name", readonly=True)
    alerted = fields.Boolean(help="Shows if notification email for course was sent")
    employee_id = fields.Many2one("hr.employee", readonly=True)
    course_start = fields.Date(related="course_schedule_id.start_date", readonly=True)
    course_end = fields.Date(related="course_schedule_id.end_date", readonly=True)
    state = fields.Selection(related="course_schedule_id.state", readonly=True)
    result = fields.Selection(
        [
            ("passed", "Passed"),
            ("failed", "Failed"),
            ("absent", "Absent"),
            ("pending", "Pending"),
        ],
        string="Result",
        default="pending",
    )
    active = fields.Boolean(default=True, readonly=True)

    def _remove_from_course(self):
        return [(1, self.id, {"active": False})]


class HrCourse(models.Model):
    _name = "hr.course"
    _description = "Course"
    _inherit = "mail.thread"

    name = fields.Char(string="Name", required=True, tracking=True)
    category_id = fields.Many2one(
        "hr.course.category", string="Category", required=True
    )

    permanence = fields.Boolean(
        string="Has Permanence",
        readonly=True,
        default=False,
        tracking=True,
    )
    permanence_time = fields.Char(
        string="Permanence time",
        readonly=True,
        tracking=True,
    )

    alerted = fields.Boolean()
    content = fields.Html()
    objective = fields.Html()
    validity_end_date = fields.Date()
    evaluation_criteria = fields.Html()

    course_schedule_ids = fields.One2many(
        "hr.course.schedule",
        inverse_name="course_id",
        readonly=True,
    )

    course_attendee_ids = fields.One2many(
        related="course_schedule_ids.course_attendee_ids"
    )

    @api.model
    def send_course_notification_email(self):
        company_id = self.env.context.get("company_id") or self.env.company.id
        channel = (
            self.env["res.company"].browse(company_id).course_expiration_channel_id
        )
        email_template = self.env.ref("hr_course.mail_template_validity_reminder")

        if channel and self._name == "hr.course":
            channel.with_context(
                recipient_ids=channel.channel_last_seen_partner_ids.mapped(
                    "partner_email"
                ),
                email_from=channel.alias_id.display_name,
            ).message_post_with_template(
                template_id=email_template.id, res_id=self.id, model="hr.course"
            )
        return True

    @api.model
    def process_validity(self):
        company_id = self.env.context.get("company_id") or self.env.company.id
        course_expiration_alerting_delay = (
            self.env["res.company"].browse(company_id).course_expiration_alerting_delay
        )

        for course in self:
            if course.validity_end_date:

                if (
                    course.validity_end_date
                    - timedelta(days=course_expiration_alerting_delay)
                    <= fields.Date.today()
                ):
                    course.alerted = True
                    course.send_course_notification_email()

    def _cron_check_validity_date(self):
        items = self.search([("alerted", "=", False)])
        items.process_validity()

    @api.onchange("permanence")
    def _onchange_permanence(self):
        self.permanence_time = False


class HRCourseCategory(models.Model):
    _name = "hr.course.category"
    _description = "Course Category"

    name = fields.Char(string="Course category", required=True)

    _sql_constraints = [("name_uniq", "unique (name)", "Category already exists !")]
