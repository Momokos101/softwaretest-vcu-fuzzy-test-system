import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend"))

from api.models.schemas import ExportFormat, ExportRequest, ExportScope
from api.services import export_service, requirement_service
from api.services.llm_client import get_llm_config


class AutoTestDesignV2ServiceTests(unittest.TestCase):
    def test_llm_config_reads_environment(self):
        os.environ["LLM_PROVIDER"] = "openai_compatible"
        os.environ["LLM_BASE_URL"] = "http://localhost:11434/v1"
        os.environ["LLM_API_KEY"] = "test-key"
        os.environ["LLM_MODEL"] = "qwen-test"

        config = get_llm_config()

        self.assertEqual(config.provider, "openai_compatible")
        self.assertEqual(config.base_url, "http://localhost:11434/v1")
        self.assertEqual(config.api_key, "test-key")
        self.assertEqual(config.model, "qwen-test")

    def test_demo_requirements_are_v2_complete(self):
        requirements = requirement_service.load_demo_requirements(replace=True)

        self.assertEqual(len(requirements), 24)
        self.assertEqual(requirements[0].id, "REQ-001")
        self.assertEqual(requirements[-1].id, "REQ-024")

    def test_export_includes_requirements_and_traceability(self):
        requirement_service.load_demo_requirements(replace=True)

        content, media_type, filename = export_service.export_data(
            ExportRequest(format=ExportFormat.JSON, scope=ExportScope())
        )

        self.assertEqual(media_type, "application/json")
        self.assertEqual(filename, "autotestdesign_v2_export.json")
        self.assertIn(b"REQ-001", content)


if __name__ == "__main__":
    unittest.main()
