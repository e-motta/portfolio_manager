from dataclasses import dataclass


@dataclass
class ResultSingle:
    data: dict | None = None
    message: str | None = None


@dataclass
class ResultMultiple:
    data: list[dict] | None = None
    message: str | None = None
