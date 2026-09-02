"""End-to-end tests for ovos-skill-pyradios (OCP skill)."""
from unittest import TestCase

from ovoscope import get_minicroft


class TestSkillLoads(TestCase):
    """Verify the skill plugin loads and reaches READY state."""

    @classmethod
    def setUpClass(cls):
        cls.skill_id = "ovos-skill-pyradios.openvoiceos"
        cls.minicroft = get_minicroft([cls.skill_id])

    @classmethod
    def tearDownClass(cls):
        if cls.minicroft:
            cls.minicroft.stop()

    def test_skill_loaded(self):
        """Skill must appear in the loaded plugin skills."""
        self.assertIn(self.skill_id, self.minicroft.plugin_skills)
