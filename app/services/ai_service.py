from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class AIAnalysisResult:
    scene_label: str | None = None
    location_guess: str | None = None
    description: str | None = None
    confidence: float | None = None
    tags: list[str] | None = None


class BaseVisionAnalyzer:
    def analyze(self, image_path: Path) -> AIAnalysisResult:
        raise NotImplementedError


class PlaceholderVisionAnalyzer(BaseVisionAnalyzer):
    def analyze(self, image_path: Path) -> AIAnalysisResult:
        # MVP 只保留统一接口，后续替换为本地模型时业务层无需改动。
        return AIAnalysisResult(
            scene_label=None,
            location_guess=None,
            description=None,
            confidence=None,
            tags=[],
        )


vision_analyzer: BaseVisionAnalyzer = PlaceholderVisionAnalyzer()
