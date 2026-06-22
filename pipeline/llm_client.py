import os
import time
import json
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, GoogleAPIError
from dotenv import load_dotenv

load_dotenv()

# Model name mapping: generic names -> actual Gemini models
MODEL_ALIASES = {
    "gpt-4o": "gemini-2.0-flash",
    "gpt-4o-mini": "gemini-2.0-flash",
    "gpt-3.5-turbo": "gemini-1.5-flash",
}


class LLMClient:
    def __init__(self, model: str | None = None, max_retries: int = 2):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable not set. "
                "Set it in your environment or create a .env file."
            )
        genai.configure(api_key=api_key)

        model_name = model or os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        self.model_name = MODEL_ALIASES.get(model_name, model_name)
        self.max_retries = max_retries

    def _truncate(self, text: str, max_chars: int = 28000) -> str:
        if len(text) <= max_chars:
            return text
        half = max_chars // 2
        return text[:half] + "\n\n...[TRUNCATED]...\n\n" + text[-half:]

    def call(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 4096,
    ) -> dict:
        user_prompt = self._truncate(user_prompt, max_chars=28000)

        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                model = genai.GenerativeModel(
                    self.model_name,
                    system_instruction=system_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=temperature,
                        max_output_tokens=max_tokens,
                    ),
                )

                start = time.time()
                response = model.generate_content(user_prompt)
                latency_ms = (time.time() - start) * 1000

                usage = response.usage_metadata
                candidate = response.candidates[0] if response.candidates else None

                return {
                    "content": response.text or "",
                    "model": self.model_name,
                    "usage": {
                        "prompt_tokens": usage.prompt_token_count if usage else 0,
                        "completion_tokens": usage.candidates_token_count if usage else 0,
                        "total_tokens": usage.total_token_count if usage else 0,
                    },
                    "latency_ms": latency_ms,
                    "finish_reason": str(candidate.finish_reason) if candidate else "unknown",
                }

            except ResourceExhausted as e:
                last_error = e
                if attempt < self.max_retries:
                    wait = 2.0 ** attempt
                    time.sleep(wait)
                continue

            except GoogleAPIError as e:
                raise RuntimeError(f"Gemini API error: {e}") from e

            except Exception as e:
                raise RuntimeError(f"Gemini call failed: {e}") from e

        raise RuntimeError(
            f"Gemini API quota exhausted after {self.max_retries + 1} attempts"
        ) from last_error

    def call_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
    ) -> dict:
        user_prompt = self._truncate(user_prompt, max_chars=28000)

        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                model = genai.GenerativeModel(
                    self.model_name,
                    system_instruction=system_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=temperature,
                        response_mime_type="application/json",
                    ),
                )

                start = time.time()
                response = model.generate_content(user_prompt)
                latency_ms = (time.time() - start) * 1000

                content = response.text or ""
                usage = response.usage_metadata
                candidate = response.candidates[0] if response.candidates else None

                # Parse JSON
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()

                result = {
                    "content": response.text or "",
                    "model": self.model_name,
                    "usage": {
                        "prompt_tokens": usage.prompt_token_count if usage else 0,
                        "completion_tokens": usage.candidates_token_count if usage else 0,
                        "total_tokens": usage.total_token_count if usage else 0,
                    },
                    "latency_ms": latency_ms,
                    "finish_reason": str(candidate.finish_reason) if candidate else "unknown",
                }

                try:
                    result["parsed"] = json.loads(content)
                except json.JSONDecodeError as e:
                    result["parsed"] = {"error": str(e), "raw": content}
                    result["parse_error"] = str(e)

                return result

            except ResourceExhausted as e:
                last_error = e
                if attempt < self.max_retries:
                    wait = 2.0 ** attempt
                    time.sleep(wait)
                continue

            except GoogleAPIError as e:
                raise RuntimeError(f"Gemini API error: {e}") from e

            except Exception as e:
                raise RuntimeError(f"Gemini call failed: {e}") from e

        raise RuntimeError(
            f"Gemini API quota exhausted after {self.max_retries + 1} attempts"
        ) from last_error
