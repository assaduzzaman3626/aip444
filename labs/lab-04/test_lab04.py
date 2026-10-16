"""Offline checks: SDK parsing uses an in-memory HTTP transport, never OpenRouter."""

import json
import os
from pathlib import Path
import unittest
from unittest.mock import AsyncMock, patch

import httpx
from fastapi.testclient import TestClient
from openai import AsyncOpenAI
from pydantic import ValidationError

import flashcard_generator as generator
from schemas import Flashcard, FlashcardResponse
import server
import test_client


NOTES = "The git status command shows the current state of the repository."
CARD = {
    "application": "A student is inspecting a project.",
    "challenge": "Which command shows repository state?",
    "answer": NOTES,
    "evidence": NOTES,
    "misconception": '"git status saves changes."',
    "correction": "The notes say it shows the repository state.",
}


class SchemaTests(unittest.TestCase):
    def test_round_trip_and_strict_json_schema(self):
        result = FlashcardResponse(flashcards=[Flashcard(**CARD)])
        self.assertEqual(FlashcardResponse.model_validate_json(result.model_dump_json()), result)
        schema = FlashcardResponse.model_json_schema()
        self.assertFalse(schema["additionalProperties"])
        self.assertFalse(schema["$defs"]["Flashcard"]["additionalProperties"])
        self.assertEqual(set(schema["$defs"]["Flashcard"]["required"]), set(CARD))

    def test_missing_extra_wrong_type_and_empty_field(self):
        for card in ({k: v for k, v in CARD.items() if k != "answer"},
                     dict(CARD, unexpected="value"), dict(CARD, answer=123), dict(CARD, evidence="")):
            with self.subTest(card=card), self.assertRaises(ValidationError):
                Flashcard.model_validate(card)


class GeneratorTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        for patcher in (
            patch.dict(os.environ, {"OPENROUTER_API_KEY": "fake-test-key", "OPENROUTER_MODEL": "test/model"}, clear=True),
            patch.object(generator, "load_dotenv"),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)
        self.payload = {"flashcards": [CARD]}
        self.refusal = None
        self.status = 200
        self.requests = []

    def transport(self, request):
        self.requests.append(json.loads(request.content))
        if self.status != 200:
            return httpx.Response(self.status, json={"error": {"message": "fake-test-key"}})
        return httpx.Response(200, json={
            "id": "test", "object": "chat.completion", "created": 0, "model": "test/model",
            "choices": [{"index": 0, "finish_reason": "stop", "message": {
                "role": "assistant", "content": json.dumps(self.payload), "refusal": self.refusal,
            }}],
            "usage": {"prompt_tokens": 20, "completion_tokens": 40, "total_tokens": 60, "cost": 0.001},
        })

    async def call_generator(self, notes=NOTES, cards=1):
        # Keep the real SDK and its Pydantic parsing; replace only HTTP transport.
        client = AsyncOpenAI(api_key="fake-test-key", base_url="https://openrouter.ai/api/v1",
                             max_retries=0, http_client=httpx.AsyncClient(transport=httpx.MockTransport(self.transport)))
        with patch.object(generator, "AsyncOpenAI", return_value=client):
            return await generator.generate_flashcards(notes, cards)

    async def test_actual_sdk_parse_and_payload(self):
        with self.assertLogs(generator.logger, level="INFO") as logs:
            result = await self.call_generator()
        self.assertIsInstance(result, FlashcardResponse)
        self.assertEqual(result.flashcards[0].evidence, NOTES)
        payload = self.requests[0]
        self.assertEqual(payload["response_format"]["type"], "json_schema")
        self.assertTrue(payload["response_format"]["json_schema"]["strict"])
        self.assertEqual(payload["model"], "test/model")
        self.assertEqual(payload["messages"][0]["content"],
                         (generator.LAB_DIR / "SYSTEM_PROMPT.md").read_text(encoding="utf-8"))
        self.assertEqual(json.loads(payload["messages"][1]["content"]), {"notes": NOTES, "cards": 1})
        self.assertNotIn("fake-test-key", " ".join(logs.output))
        self.assertIn("cost_usd=0.001", " ".join(logs.output))

    async def test_grounding_regression_rules_reach_model(self):
        # Check prompt delivery, not whether a mocked model learned the rules.
        await self.call_generator()
        prompt = self.requests[0]["messages"][0]["content"]
        for rule in (
            "Avoid absolute claims and unsupported wording in answers and corrections.",
            "notes explicitly support that scope",
            "cannot be used without a new git add",
            "history is permanently unchangeable",
            "omit unsupported additions",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, prompt)

    async def test_invalid_inputs_do_not_call_provider(self):
        with patch.object(generator, "AsyncOpenAI") as sdk:
            for notes, cards in ((" ", 1), (NOTES, 0), (NOTES, 21), (NOTES, True)):
                with self.subTest(cards=cards), self.assertRaises(ValueError):
                    await generator.generate_flashcards(notes, cards)
            sdk.assert_not_called()

    async def test_missing_configuration(self):
        for variable in ("OPENROUTER_API_KEY", "OPENROUTER_MODEL"):
            with self.subTest(variable=variable), patch.dict(os.environ, {variable: ""}):
                with self.assertRaisesRegex(RuntimeError, variable):
                    await generator.generate_flashcards(NOTES, 1)

    async def test_provider_errors_hide_secret(self):
        for status in (401, 402, 429, 500):
            self.status = status
            with self.subTest(status=status), self.assertRaises(RuntimeError) as caught:
                await self.call_generator()
            self.assertNotIn("fake-test-key", str(caught.exception))

    async def test_wrong_count(self):
        self.payload = {"flashcards": []}
        with self.assertRaisesRegex(RuntimeError, "requested number"):
            await self.call_generator()

    async def test_fabricated_evidence(self):
        self.payload = {"flashcards": [dict(CARD, evidence="Invented quote.")]}
        with self.assertRaisesRegex(RuntimeError, "quotation"):
            await self.call_generator()

    async def test_malformed_structured_output(self):
        self.payload = {"flashcards": [{"answer": "missing fields"}]}
        with self.assertRaisesRegex(RuntimeError, "invalid structured output"):
            await self.call_generator()

    async def test_refusal(self):
        self.refusal = "Cannot generate."
        with self.assertRaisesRegex(RuntimeError, "declined"):
            await self.call_generator()

    async def test_timeout(self):
        async def timeout(request):
            raise httpx.ReadTimeout("fake-test-key", request=request)
        with patch.object(self, "transport", side_effect=timeout):
            with self.assertRaisesRegex(RuntimeError, "provider request failed"):
                await self.call_generator()


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(server.app)
        self.addCleanup(self.client.close)

    def test_post_json_and_default_count(self):
        result = FlashcardResponse(flashcards=[Flashcard(**CARD)])
        with patch.object(server, "generate_flashcards", new_callable=AsyncMock, return_value=result) as generate:
            response = self.client.post("/api/generate", json={"notes": NOTES})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), result.model_dump())
        generate.assert_awaited_once_with(NOTES, 3)
        self.assertGreaterEqual(float(response.headers["X-Process-Time"]), 0)

    def test_missing_notes_and_invalid_count_type(self):
        with patch.object(server, "generate_flashcards", new_callable=AsyncMock) as generate:
            for payload in ({"cards": 2}, {"notes": NOTES, "cards": "not a number"}):
                self.assertEqual(self.client.post("/api/generate", json=payload).status_code, 422)
        generate.assert_not_awaited()

    def test_cors_preflight(self):
        response = self.client.options("/api/generate", headers={
            "Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["access-control-allow-origin"], "*")

    def test_safe_generation_failure(self):
        with patch.object(server, "generate_flashcards", new_callable=AsyncMock,
                          side_effect=RuntimeError("Safe generation failure")), patch("builtins.print"):
            response = self.client.post("/api/generate", json={"notes": NOTES, "cards": 1})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["detail"], "Safe generation failure")


class ClientTests(unittest.TestCase):
    def test_client_success_without_network(self):
        with patch.object(Path, "read_text", return_value=NOTES), patch.object(test_client.requests, "post") as post, patch("builtins.print") as output:
            post.return_value.ok = True
            post.return_value.json.return_value = {"flashcards": [CARD]}
            self.assertEqual(test_client.test_server(cards=1), 0)
        self.assertEqual(post.call_args.kwargs["json"], {"notes": NOTES, "cards": 1})
        self.assertTrue(any("Success!" in str(call) for call in output.call_args_list))

    def test_client_http_failure(self):
        with patch.object(Path, "read_text", return_value=NOTES), patch.object(test_client.requests, "post") as post, patch("builtins.print"):
            post.return_value.ok = False
            self.assertEqual(test_client.test_server(), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
