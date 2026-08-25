from __future__ import annotations

import re
import unittest
from unittest.mock import MagicMock, patch

from questionnaire.formbricks_payload import DUMMY_WORKSPACE_ID, build_payload, logical_question_count
from scripts.create_survey import get_workspace_id


class QuestionnairePayloadTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = build_payload(DUMMY_WORKSPACE_ID)

    def iter_elements(self):
        for survey_block in self.payload["blocks"]:
            yield from survey_block["elements"]

    def test_expected_structure(self) -> None:
        self.assertEqual(len(self.payload["blocks"]), 19)
        self.assertEqual(logical_question_count(self.payload), 255)
        self.assertEqual(self.payload["defaultLanguage"], "fr-FR")
        self.assertEqual(self.payload["status"], "draft")

    def test_every_question_is_required(self) -> None:
        for element in self.iter_elements():
            self.assertTrue(element["required"], element["id"])

    def test_every_matrix_requires_every_row(self) -> None:
        matrices = [element for element in self.iter_elements() if element["type"] == "matrix"]
        self.assertGreater(len(matrices), 0)
        for element in matrices:
            rules = element["validation"]["rules"]
            self.assertIn("answerAllRows", {rule["type"] for rule in rules}, element["id"])

    def test_no_parent_fill_in_label(self) -> None:
        serialized = str(self.payload).lower()
        self.assertNotIn("à remplir par", serialized)
        self.assertNotIn("a remplir par", serialized)

    def test_question_wording_is_not_first_person(self) -> None:
        first_person = re.compile(r"\bje\b|\bj['’]|\bme\b|\bmes\b|\bmon\b|\bma\b|\bmoi\b", re.IGNORECASE)
        texts: list[str] = []
        for element in self.iter_elements():
            texts.extend(element["headline"].values())
            texts.extend(row_text for row in element.get("rows", []) for row_text in row["label"].values())
        offenders = [text for text in texts if first_person.search(text)]
        self.assertEqual(offenders, [])

    def test_each_section_has_save_button(self) -> None:
        for survey_block in self.payload["blocks"][:-1]:
            self.assertEqual(survey_block["buttonLabel"]["fr-FR"], "Enregistrer et continuer")
        self.assertEqual(self.payload["blocks"][-1]["buttonLabel"]["fr-FR"], "Envoyer mes réponses")


class FormbricksApiTests(unittest.TestCase):
    @patch("scripts.create_survey.urllib.request.urlopen")
    def test_workspace_is_detected_from_api_key(self, urlopen: MagicMock) -> None:
        response = MagicMock()
        response.read.return_value = (
            b'{"data":{"organizationId":"org-123","workspacePermissions":['
            b'{"workspaceId":"workspace-123","workspaceName":"TND","permissions":"manage"}]}}'
        )
        urlopen.return_value.__enter__.return_value = response

        workspace_id = get_workspace_id("https://app.formbricks.com", "secret-key")

        self.assertEqual(workspace_id, "workspace-123")
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://app.formbricks.com/api/v2/me")
        self.assertEqual(request.get_header("X-api-key"), "secret-key")
        self.assertEqual(request.get_header("User-agent"), "tnd-questionnaire-import/1.0")
        self.assertIsNotNone(urlopen.call_args.kwargs["context"])


if __name__ == "__main__":
    unittest.main()
