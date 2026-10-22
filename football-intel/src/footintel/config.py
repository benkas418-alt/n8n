"""Runtime settings, read from environment variables and an optional .env file."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class PromotionCriteria(BaseSettings):
    """Thresholds a candidate model must meet. They are fixed before any evaluation."""

    model_config = SettingsConfigDict(env_prefix="PROMOTION_", env_file=".env", extra="ignore")

    min_test_matches: int = 300
    # Candidate log loss must be at least this much lower than the reference.
    min_logloss_improvement: float = 0.002
    # Upper bound of the bootstrap CI of (candidate - reference) log loss must be below 0.
    require_ci_below_zero: bool = True
    bootstrap_samples: int = 1000
    # Secondary route, fixed on 2026-10-22 before any goal-model result was seen:
    # a candidate that does not degrade 1X2 (mean diff <= max_1x2_degradation) is
    # promoted if its over/under 2.5 log loss gains at least min_goal_improvement
    # with a bootstrap CI entirely below 0.
    goals_secondary: bool = True
    max_1x2_degradation: float = 0.0005
    min_goal_improvement: float = 0.002


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://footintel:footintel_dev@localhost:5432/footintel"
    api_football_key: SecretStr | None = None
    api_football_base_url: str = "https://v3.football.api-sports.io"
    # football-data.org free plan: 10 requests per minute, header X-Auth-Token.
    football_data_org_key: SecretStr | None = None
    admin_token: SecretStr | None = None

    data_dir: Path = Path("./data")
    artifacts_dir: Path = Path("./artifacts")
    reports_dir: Path = Path("./reports")
    timezone: str = "Africa/Lubumbashi"

    http_timeout_seconds: float = 20.0
    http_max_retries: int = 3
    # Minimum delay between two requests to the same host.
    http_min_interval_seconds: float = 1.0
    user_agent: str = "footintel/0.1 (personal research project)"

    # A team needs this many prior matches before its prediction is "sufficient".
    min_prior_matches: int = 5

    telegram_bot_token: SecretStr | None = None
    telegram_chat_id: str | None = None

    promotion: PromotionCriteria = Field(default_factory=PromotionCriteria)

    @property
    def football_data_org_enabled(self) -> bool:
        return bool(self.football_data_org_key and self.football_data_org_key.get_secret_value().strip())

    @property
    def api_football_enabled(self) -> bool:
        return bool(self.api_football_key and self.api_football_key.get_secret_value().strip())


@lru_cache
def get_settings() -> Settings:
    return Settings()
