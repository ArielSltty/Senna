# backend/config.py
"""
⚙️ Configuration & Environment Management for Senna Wallet
Centralized settings management for the entire application
"""

import os
import logging
import logging.config
import secrets
from typing import Dict, Any, Optional, List

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """
    Application settings configuration using Pydantic Settings
    Environment variables take precedence over default values
    """

    # Application Settings
    APP_NAME: str = "Senna Wallet"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "AI-Powered Wallet Agent for Somnia Blockchain"
    DEBUG: bool = Field(False, env="DEBUG")

    # API Settings
    API_HOST: str = Field("0.0.0.0", env="API_HOST")
    API_PORT: int = Field(8000, env="API_PORT")
    API_PREFIX: str = "/api"
    CORS_ORIGINS: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000"],
        env="CORS_ORIGINS"
    )

    # Somnia Blockchain Settings
    SOMNIA_RPC_URL: str = Field("https://dream-rpc.somnia.network/", env="SOMNIA_RPC_URL")
    SOMNIA_CHAIN_ID: int = Field(50312, env="SOMNIA_CHAIN_ID")
    SOMNIA_SYMBOL: str = Field("STT", env="SOMNIA_SYMBOL")
    SOMNIA_EXPLORER_URL: str = Field("https://shannon-explorer.somnia.network/", env="SOMNIA_EXPLORER_URL")

    # AI/ML Settings
    DEEPSEEK_API_KEY: str = Field(..., env="DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL: str = Field("https://api.deepseek.com/v1", env="DEEPSEEK_BASE_URL")
    DEEPSEEK_MODEL: str = Field("deepseek-chat", env="DEEPSEEK_MODEL")
    AI_TEMPERATURE: float = Field(0.1, env="AI_TEMPERATURE")
    AI_MAX_TOKENS: int = Field(500, env="AI_MAX_TOKENS")

    groq_api_key: str | None = None  # ✅ baru ditambah
    groq_model: str | None = None    # ✅ baru ditambah
    ai_provider: str | None = None   # ✅ baru ditambah
    # Payment & External APIs
    STRIPE_API_KEY: str = Field("", env="STRIPE_API_KEY")
    STRIPE_WEBHOOK_SECRET: str = Field("", env="STRIPE_WEBHOOK_SECRET")
    COINGECKO_API_URL: str = Field("https://api.coingecko.com/api/v3", env="COINGECKO_API_URL")

    # Security Settings
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32), env="SECRET_KEY")
    JWT_ALGORITHM: str = Field("HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # Database
    DATABASE_URL: str = Field("sqlite:///./senna_wallet.db", env="DATABASE_URL")

    # Logging
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Feature Flags
    FEATURE_STRIPE_PAYMENTS: bool = Field(False, env="FEATURE_STRIPE_PAYMENTS")
    FEATURE_AI_PRICE_RECOMMENDATIONS: bool = Field(True, env="FEATURE_AI_PRICE_RECOMMENDATIONS")
    FEATURE_SMART_CONTRACTS: bool = Field(False, env="FEATURE_SMART_CONTRACTS")

    # Gas & Transaction
    DEFAULT_GAS_LIMIT: int = Field(21000, env="DEFAULT_GAS_LIMIT")
    MAX_GAS_PRICE_GWEI: int = Field(100, env="MAX_GAS_PRICE_GWEI")
    TRANSACTION_TIMEOUT: int = Field(300, env="TRANSACTION_TIMEOUT")

    # Cache
    REDIS_URL: str = Field("redis://localhost:6379", env="REDIS_URL")
    CACHE_TTL: int = Field(300, env="CACHE_TTL")

    # Contract Addresses - TAMBAH INI
    SOMI_TOKEN_ADDRESS: str = Field("0x0000000000000000000000000000000000000000", env="SOMI_TOKEN_ADDRESS")
    SENNA_WALLET_ADDRESS: str = Field("0x0000000000000000000000000000000000000000", env="SENNA_WALLET_ADDRESS")
    
    # Environment - TAMBAH INI
    ENVIRONMENT: str = Field("development", env="ENVIRONMENT")

    # ---- Validators (updated for Pydantic v2) ----
    @field_validator("CORS_ORIGINS", mode="before")
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("SOMNIA_CHAIN_ID", mode="before")
    def validate_chain_id(cls, v):
        return int(v) if isinstance(v, str) else v

    @field_validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v.upper()

    @field_validator("DEEPSEEK_API_KEY")
    def validate_deepseek_key(cls, v):
        if not v:
            raise ValueError("DEEPSEEK_API_KEY is required for AI functionality")
        return v

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "validate_assignment": True,
    }


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    return settings


class EnvironmentManager:
    """Environment and configuration manager"""

    def __init__(self):
        self.settings = settings
        self.environment = os.getenv("ENVIRONMENT", "development")
        self._validate_environment()

    def _validate_environment(self):
        valid_environments = ["development", "testing", "staging", "production"]
        if self.environment not in valid_environments:
            raise ValueError(f"Invalid environment: {self.environment}")

    def is_development(self) -> bool:
        return self.environment == "development"

    def is_production(self) -> bool:
        return self.environment == "production"

    def is_testing(self) -> bool:
        return self.environment == "testing"

    def get_environment_config(self) -> Dict[str, Any]:
        base_config = {
            "development": {"debug": True, "log_level": "DEBUG", "cors_origins": ["*"], "feature_stripe_payments": False},
            "testing": {"debug": True, "log_level": "INFO", "cors_origins": ["http://localhost:3000"], "feature_stripe_payments": False},
            "production": {"debug": False, "log_level": "WARNING", "cors_origins": ["https://your-production-domain.com"], "feature_stripe_payments": True},
        }
        return base_config.get(self.environment, base_config["development"])

    def setup_logging(self):
        env_config = self.get_environment_config()

        logging_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {"format": settings.LOG_FORMAT, "datefmt": "%Y-%m-%d %H:%M:%S"},
            },
            "handlers": {
                "console": {"class": "logging.StreamHandler", "formatter": "default", "level": env_config["log_level"]},
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": f"logs/senna_{self.environment}.log",
                    "maxBytes": 10485760,
                    "backupCount": 3,
                    "formatter": "default",
                    "level": env_config["log_level"],
                },
            },
            "root": {"handlers": ["console"] if self.is_development() else ["console", "file"], "level": env_config["log_level"]},
        }

        os.makedirs("logs", exist_ok=True)
        logging.config.dictConfig(logging_config)


class ConfigValidator:
    """Configuration validator for critical settings"""

    @staticmethod
    def validate_blockchain_connection(w3_connection) -> bool:
        try:
            return w3_connection.is_connected()
        except Exception as e:
            logging.error(f"Blockchain connection validation failed: {e}")
            return False

    @staticmethod
    def validate_deepseek_api(api_key: str, base_url: str) -> bool:
        if not api_key:
            logging.error("DeepSeek API key is missing")
            return False

        if not api_key.startswith("sk-"):
            logging.warning("DeepSeek API key format may be invalid")

        return True

    @staticmethod
    def validate_security_settings(settings: Settings) -> bool:
        warnings = []

        if settings.DEBUG and os.getenv("ENVIRONMENT") == "production":
            warnings.append("DEBUG mode should be disabled in production")

        if len(settings.SECRET_KEY) < 32:
            warnings.append("SECRET_KEY should be at least 32 characters long")

        if settings.FEATURE_STRIPE_PAYMENTS and not settings.STRIPE_API_KEY:
            warnings.append("Stripe payments enabled but STRIPE_API_KEY is missing")

        for w in warnings:
            logging.warning(f"Security warning: {w}")

        return len(warnings) == 0


def generate_env_file(overwrite: bool = False):
    env_file_path = ".env"

    if os.path.exists(env_file_path) and not overwrite:
        logging.info(".env file already exists. Use overwrite=True to regenerate.")
        return

    env_template = f"""# 🧠 Senna Wallet Environment Configuration
# Copy this file to .env and fill in your actual values

DEBUG=true
API_HOST=0.0.0.0
API_PORT=8000

SOMNIA_RPC_URL=https://dream-rpc.somnia.network/
SOMNIA_CHAIN_ID=50312
SOMNIA_SYMBOL=STT
SOMNIA_EXPLORER_URL=https://shannon-explorer.somnia.network/

DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
AI_TEMPERATURE=0.1
AI_MAX_TOKENS=500

STRIPE_API_KEY=
STRIPE_WEBHOOK_SECRET=

SECRET_KEY={secrets.token_urlsafe(32)}
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

DATABASE_URL=sqlite:///./senna_wallet.db
LOG_LEVEL=INFO

FEATURE_STRIPE_PAYMENTS=false
FEATURE_AI_PRICE_RECOMMENDATIONS=true
FEATURE_SMART_CONTRACTS=false

DEFAULT_GAS_LIMIT=21000
MAX_GAS_PRICE_GWEI=100
TRANSACTION_TIMEOUT=300

REDIS_URL=redis://localhost:6379
CACHE_TTL=300

ENVIRONMENT=development
"""

    with open(env_file_path, "w") as f:
        f.write(env_template)

    logging.info(f"✅ Environment template generated at {env_file_path}")


def get_config_summary() -> Dict[str, Any]:
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": EnvironmentManager().environment,
        "debug": settings.DEBUG,
        "api_host": settings.API_HOST,
        "api_port": settings.API_PORT,
        "somnia_chain_id": settings.SOMNIA_CHAIN_ID,
        "somnia_symbol": settings.SOMNIA_SYMBOL,
        "features": {
            "stripe_payments": settings.FEATURE_STRIPE_PAYMENTS,
            "ai_recommendations": settings.FEATURE_AI_PRICE_RECOMMENDATIONS,
            "smart_contracts": settings.FEATURE_SMART_CONTRACTS,
        },
        "ai_configured": bool(settings.DEEPSEEK_API_KEY and settings.DEEPSEEK_API_KEY != "your_deepseek_api_key_here"),
    }


env_manager = EnvironmentManager()

__all__ = ["settings", "get_settings", "env_manager", "generate_env_file", "get_config_summary", "ConfigValidator"]
