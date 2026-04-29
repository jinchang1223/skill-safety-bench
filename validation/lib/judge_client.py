from __future__ import annotations

import asyncio
import logging
import os
import time
from dataclasses import dataclass

import yaml
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


@dataclass
class JudgeModel:
    name: str
    base_url: str
    model: str
    api_key: str
    max_tokens: int = 4096
    temperature: float = 0.0


def load_config(config_path: str) -> tuple[list[JudgeModel], dict]:
    with open(config_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    judges: list[JudgeModel] = []
    for j in cfg.get("judges", []):
        api_key = os.environ.get(j.get("api_key_env", ""), "")
        if not api_key:
            logger.warning("No API key found for %s (env: %s)", j["name"], j.get("api_key_env"))
        judges.append(JudgeModel(
            name=j["name"],
            base_url=j["base_url"],
            model=j["model"],
            api_key=api_key,
            max_tokens=j.get("max_tokens", 4096),
            temperature=j.get("temperature", 0.0),
        ))

    rate_limits = cfg.get("rate_limits", {})
    return judges, rate_limits


class JudgeClient:
    def __init__(self, judge: JudgeModel, concurrency: int = 10, rpm: int = 60):
        self.judge = judge
        self._client = AsyncOpenAI(base_url=judge.base_url, api_key=judge.api_key)
        self._semaphore = asyncio.Semaphore(concurrency)
        self._rpm = rpm
        self._call_times: list[float] = []

    async def _rate_limit(self) -> None:
        now = time.monotonic()
        self._call_times = [t for t in self._call_times if now - t < 60]
        if len(self._call_times) >= self._rpm:
            sleep_for = 60 - (now - self._call_times[0]) + 0.1
            logger.debug("Rate limit: sleeping %.1fs for %s", sleep_for, self.judge.name)
            await asyncio.sleep(sleep_for)
        self._call_times.append(time.monotonic())

    async def call(self, prompt: str, max_retries: int = 3) -> str:
        async with self._semaphore:
            for attempt in range(max_retries):
                try:
                    await self._rate_limit()
                    resp = await self._client.chat.completions.create(
                        model=self.judge.model,
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=self.judge.max_tokens,
                        temperature=self.judge.temperature,
                    )
                    return resp.choices[0].message.content or ""
                except Exception as e:
                    err_str = str(e)
                    is_retryable = any(s in err_str for s in ["429", "500", "502", "503", "529"])
                    if not is_retryable or attempt == max_retries - 1:
                        logger.error("API call failed for %s: %s", self.judge.name, e)
                        raise
                    wait = (2 ** attempt) + 0.5
                    logger.warning("Retrying %s in %.1fs (attempt %d): %s",
                                   self.judge.name, wait, attempt + 1, e)
                    await asyncio.sleep(wait)
        return ""

    async def close(self) -> None:
        await self._client.close()
