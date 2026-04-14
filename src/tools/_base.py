from typing import Any

from pydantic_settings import BaseSettings


class Tool:
    class Config(BaseSettings):
        pass

    _cfg: Any = None

    @staticmethod
    def run(*args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError
