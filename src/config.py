import logging
import os
import re
import sys
from pathlib import Path
from typing import Any, Callable, Literal

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

import tools as _tools  # noqa: F401 — triggers subclass registration
from tools._base import Tool


def _to_snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)

logger = logging.getLogger("monoclaw-tools")


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TOOLS__")
    name: str = "monoclaw-tools"
    host: str = "0.0.0.0"
    port: int = 8766
    transport: Literal["stdio", "sse", "streamable-http"] = "streamable-http"
    enabled: list[str] = []

    @field_validator("enabled", mode="before")
    @classmethod
    def parse_comma_separated(cls, v: object) -> object:
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return v

    @property
    def tools(self) -> list[tuple[str, Callable[..., Any]]]:
        registry = {_to_snake(cls.__name__): cls for cls in Tool.__subclasses__()}
        specs = self.enabled or list(registry)
        if unknown := [s for s in specs if s not in registry]:
            logger.error(f"unknown tools: {unknown!r}")
            sys.exit(1)
        result = []
        for name in specs:
            cls = registry[name]
            try:
                cls._cfg = cls.Config(_env_prefix=f"TOOLS__{name.upper()}__")  # type: ignore[call-arg]
            except Exception as exc:
                logger.error(f"{name} config validation failed: {exc}")
                sys.exit(1)
            result.append((name, cls.run))
        return result


cfg = Config()
