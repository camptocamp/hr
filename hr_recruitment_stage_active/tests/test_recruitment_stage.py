# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestRecruitmentStage(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.RecruitmentStage = cls.env["hr.recruitment.stage"]

    def test_01_recruitment_stage(self):
        stage = self.RecruitmentStage.create({"name": "Overloaded"})
        self.assertTrue(stage.active, "Stage should be active by default")
        stage.action_archive()
        self.assertFalse(stage.active, "Stage should be inactive after archiving")
