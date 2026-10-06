import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from kb import kb


class KnowledgeBaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.temporary.name)
        kb.init(self.data_dir, ROOT / "kb" / "seed")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_init_list_and_grounded_answer(self) -> None:
        listing = kb.list_documents(self.data_dir)
        self.assertEqual(
            [item["id"] for item in listing["documents"]],
            ["architecture-notes", "retrieval-plan", "team-meeting"],
        )
        answer = kb.ask(self.data_dir, "How must deletion update state?")
        self.assertTrue(answer["citations"])
        self.assertTrue(
            all({"document", "line", "text"} <= item.keys() for item in answer["citations"])
        )

    def test_cli_list_prints_compact_json(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = kb.main([str(self.data_dir), "list"])
        self.assertEqual(exit_code, 0)
        self.assertEqual(output.getvalue().strip(), kb.compact(kb.list_documents(self.data_dir)))
