"""Central settings. Everything configurable comes from env, with sane defaults."""
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    min_delay: float = float(os.getenv("SCRAPE_MIN_DELAY_SECONDS", "1.0"))
    max_retries: int = int(os.getenv("SCRAPE_MAX_RETRIES", "3"))
    telegram_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat: str = os.getenv("TELEGRAM_CHAT_ID", "")

    # mining gates — the anti-self-deception constants
    min_n_train: int = 400
    min_n_valid: int = 120
    min_roi_train: float = 3.0     # %
    min_roi_valid: float = 0.0     # must break even OOS
    wilson_z: float = 1.645
    bench_tolerance: float = 0.08  # live LB this far below certified hit -> bench


settings = Settings()
