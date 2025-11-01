# backend/config.py
"""
⚙️ Advanced Configuration & Environment Management for Senna Wallet
Sophisticated settings management with enhanced security and features
"""

import os
import logging
import logging.config
import secrets
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field, field_validator, ConfigDict
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()


class AdvancedSettings(BaseSettings):
    """
    Advanced application settings configuration using Pydantic Settings
    Enhanced with sophisticated features and security
    """

    # Application Settings
    APP_NAME: str = "Senna Wallet AI"
    APP_VERSION: str = "2.0.0"
    APP_DESCRIPTION: str = "🧠 Advanced AI-Powered Wallet Agent for Somnia Blockchain"
    DEBUG: bool = Field(False, env="DEBUG")
    ENVIRONMENT: str = Field("development", env="ENVIRONMENT")

    # API Settings
    API_HOST: str = Field("0.0.0.0", env="API_HOST")
    API_PORT: int = Field(8000, env="API_PORT")
    API_PREFIX: str = "/api"
    CORS_ORIGINS: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000", 
            "http://127.0.0.1:3000",
            "http://localhost:8080",
            "http://127.0.0.1:8080"
        ],
        env="CORS_ORIGINS"
    )

    # Somnia Blockchain Settings
    SOMNIA_RPC_URL: str = Field("https://dream-rpc.somnia.network/", env="SOMNIA_RPC_URL")
    SOMNIA_CHAIN_ID: int = Field(50312, env="SOMNIA_CHAIN_ID")
    SOMNIA_SYMBOL: str = Field("STT", env="SOMNIA_SYMBOL")
    SOMNIA_EXPLORER_URL: str = Field("https://shannon-explorer.somnia.network/", env="SOMNIA_EXPLORER_URL")

    # Enhanced AI/ML Settings (Groq Only)
    AI_PROVIDER: str = Field("groq", env="AI_PROVIDER")
    GROQ_API_KEY: str = Field(..., env="GROQ_API_KEY")
    GROQ_BASE_URL: str = Field("https://api.groq.com/openai/v1", env="GROQ_BASE_URL")
    GROQ_MODEL: str = Field("llama-3.1-8b-instant", env="GROQ_MODEL")
    
    # Advanced AI Configuration
    AI_TEMPERATURE: float = Field(0.1, env="AI_TEMPERATURE")
    AI_MAX_TOKENS: int = Field(800, env="AI_MAX_TOKENS")
    AI_MAX_CONTEXT_LENGTH: int = Field(8000, env="AI_MAX_CONTEXT_LENGTH")
    AI_TIMEOUT: int = Field(30, env="AI_TIMEOUT")
    
    # Advanced AI Features
    AI_CONFIRMATION_FLOWS: bool = Field(True, env="AI_CONFIRMATION_FLOWS")
    AI_RISK_ANALYSIS: bool = Field(True, env="AI_RISK_ANALYSIS")
    AI_MARKET_INSIGHTS: bool = Field(True, env="AI_MARKET_INSIGHTS")
    AI_PRICE_PREDICTION: bool = Field(True, env="AI_PRICE_PREDICTION")

    # Payment & External APIs
    STRIPE_API_KEY: str = Field("", env="STRIPE_API_KEY")
    STRIPE_WEBHOOK_SECRET: str = Field("", env="STRIPE_WEBHOOK_SECRET")
    COINGECKO_API_URL: str = Field("https://api.coingecko.com/api/v3", env="COINGECKO_API_URL")

    # Enhanced Security Settings
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(64), env="SECRET_KEY")
    JWT_ALGORITHM: str = Field("HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    SESSION_TIMEOUT: int = Field(3600, env="SESSION_TIMEOUT")  # 1 hour
    
    # Advanced Security
    RATE_LIMIT_REQUESTS: int = Field(100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(60, env="RATE_LIMIT_WINDOW")  # 1 minute
    MAX_TRANSACTION_AMOUNT: float = Field(10000.0, env="MAX_TRANSACTION_AMOUNT")
    REQUIRE_TRANSACTION_CONFIRMATION: bool = Field(True, env="REQUIRE_TRANSACTION_CONFIRMATION")

    # Database & Storage
    DATABASE_URL: str = Field("sqlite:///./senna_wallet.db", env="DATABASE_URL")
    REDIS_URL: str = Field("redis://localhost:6379", env="REDIS_URL")

    # Enhanced Logging
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
    LOG_FILE: str = Field("logs/senna_advanced.log", env="LOG_FILE")
    LOG_MAX_SIZE: str = Field("10MB", env="LOG_MAX_SIZE")
    LOG_BACKUP_COUNT: int = Field(5, env="LOG_BACKUP_COUNT")

    # Advanced Feature Flags
    FEATURE_STRIPE_PAYMENTS: bool = Field(False, env="FEATURE_STRIPE_PAYMENTS")
    FEATURE_AI_PRICE_RECOMMENDATIONS: bool = Field(True, env="FEATURE_AI_PRICE_RECOMMENDATIONS")
    FEATURE_SMART_CONTRACTS: bool = Field(False, env="FEATURE_SMART_CONTRACTS")
    FEATURE_PORTFOLIO_ANALYTICS: bool = Field(True, env="FEATURE_PORTFOLIO_ANALYTICS")
    FEATURE_MARKET_PREDICTIONS: bool = Field(True, env="FEATURE_MARKET_PREDICTIONS")
    FEATURE_GAS_OPTIMIZATION: bool = Field(True, env="FEATURE_GAS_OPTIMIZATION")
    FEATURE_WEBHOOKS: bool = Field(True, env="FEATURE_WEBHOOKS")
    FEATURE_MULTI_SESSION: bool = Field(True, env="FEATURE_MULTI_SESSION")

    # Gas & Transaction Settings
    DEFAULT_GAS_LIMIT: int = Field(21000, env="DEFAULT_GAS_LIMIT")
    MAX_GAS_PRICE_GWEI: int = Field(100, env="MAX_GAS_PRICE_GWEI")
    TRANSACTION_TIMEOUT: int = Field(300, env="TRANSACTION_TIMEOUT")
    GAS_ESTIMATION_BUFFER: float = Field(1.2, env="GAS_ESTIMATION_BUFFER")

    # Cache Settings
    CACHE_TTL: int = Field(300, env="CACHE_TTL")  # 5 minutes
    PRICE_CACHE_TTL: int = Field(60, env="PRICE_CACHE_TTL")  # 1 minute for prices
    BALANCE_CACHE_TTL: int = Field(30, env="BALANCE_CACHE_TTL")  # 30 seconds for balances

    # Contract Addresses
    SOMI_TOKEN_ADDRESS: str = Field("0xc3DfbBc01Ed164F5f5b4E6B1501B20FfC9B3a49a", env="SOMI_TOKEN_ADDRESS")
    SENNA_WALLET_ADDRESS: str = Field("0x2279aB0dC1AbfCfB1D1cF93360268Fd6C31E8f0E", env="SENNA_WALLET_ADDRESS")

    # Risk Management
    RISK_HIGH_AMOUNT_THRESHOLD: float = Field(1000.0, env="RISK_HIGH_AMOUNT_THRESHOLD")
    RISK_NEW_ADDRESS_CHECK: bool = Field(True, env="RISK_NEW_ADDRESS_CHECK")
    RISK_MARKET_VOLATILITY_THRESHOLD: float = Field(0.1, env="RISK_MARKET_VOLATILITY_THRESHOLD")

    # Performance Settings
    REQUEST_TIMEOUT: int = Field(30, env="REQUEST_TIMEOUT")
    MAX_WORKERS: int = Field(10, env="MAX_WORKERS")
    BACKGROUND_TASK_INTERVAL: int = Field(300, env="BACKGROUND_TASK_INTERVAL")  # 5 minutes

    # UI/UX Settings
    CHAT_HISTORY_LIMIT: int = Field(100, env="CHAT_HISTORY_LIMIT")
    AUTO_COMPLETE_SUGGESTIONS: bool = Field(True, env="AUTO_COMPLETE_SUGGESTIONS")
    TRANSACTION_PREVIEWS: bool = Field(True, env="TRANSACTION_PREVIEWS")
    MARKET_ALERTS: bool = Field(True, env="MARKET_ALERTS")

    # Monitoring & Analytics
    ENABLE_METRICS: bool = Field(True, env="ENABLE_METRICS")
    METRICS_PORT: int = Field(9090, env="METRICS_PORT")
    HEALTH_CHECK_INTERVAL: int = Field(30, env="HEALTH_CHECK_INTERVAL")

    # ---- Advanced Validators ----
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

    @field_validator("GROQ_API_KEY")
    def validate_groq_key(cls, v):
        if not v or v == "your_groq_api_key_here":
            raise ValueError("GROQ_API_KEY is required for AI functionality")
        if not v.startswith("gsk_"):
            logging.warning("Groq API key format may be invalid")
        return v

    @field_validator("ENVIRONMENT")
    def validate_environment(cls, v):
        valid_environments = ["development", "testing", "staging", "production"]
        if v not in valid_environments:
            raise ValueError(f"ENVIRONMENT must be one of {valid_environments}")
        return v

    @field_validator("SECRET_KEY")
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v

    @field_validator("MAX_TRANSACTION_AMOUNT")
    def validate_max_transaction_amount(cls, v):
        if v <= 0:
            raise ValueError("MAX_TRANSACTION_AMOUNT must be positive")
        return v

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        validate_assignment=True,
        extra="ignore"
    )


# Global settings instance
settings = AdvancedSettings()


def get_settings() -> AdvancedSettings:
    """Get global settings instance"""
    return settings


class AdvancedEnvironmentManager:
    """Advanced environment and configuration manager with sophisticated features"""

    def __init__(self):
        self.settings = settings
        self.environment = settings.ENVIRONMENT
        self._config_cache = {}
        self._validate_advanced_environment()

    def _validate_advanced_environment(self):
        """Validate environment with advanced checks"""
        valid_environments = ["development", "testing", "staging", "production"]
        if self.environment not in valid_environments:
            raise ValueError(f"Invalid environment: {self.environment}")

        # Environment-specific validations
        if self.is_production():
            self._validate_production_settings()
        elif self.is_development():
            self._validate_development_settings()

    def _validate_production_settings(self):
        """Validate production environment settings"""
        warnings = []
        
        if self.settings.DEBUG:
            warnings.append("DEBUG mode should be disabled in production")
        
        if self.settings.SECRET_KEY == "generate_secure_random_key_here":
            warnings.append("SECRET_KEY should be properly set in production")
        
        if not self.settings.GROQ_API_KEY or self.settings.GROQ_API_KEY.startswith("your_"):
            warnings.append("GROQ_API_KEY must be properly configured in production")
        
        for warning in warnings:
            logging.warning(f"Production configuration warning: {warning}")

    def _validate_development_settings(self):
        """Validate development environment settings"""
        if not self.settings.DEBUG:
            logging.info("Consider enabling DEBUG mode for development")

    def is_development(self) -> bool:
        return self.environment == "development"

    def is_production(self) -> bool:
        return self.environment == "production"

    def is_testing(self) -> bool:
        return self.environment == "testing"

    def is_staging(self) -> bool:
        return self.environment == "staging"

    def get_environment_config(self) -> Dict[str, Any]:
        """Get comprehensive environment-specific configuration"""
        base_config = {
            "development": {
                "debug": True,
                "log_level": "DEBUG",
                "cors_origins": ["*"],
                "feature_stripe_payments": False,
                "enable_metrics": True,
                "cache_ttl": 60  # Shorter cache for development
            },
            "testing": {
                "debug": True,
                "log_level": "INFO",
                "cors_origins": ["http://localhost:3000"],
                "feature_stripe_payments": False,
                "enable_metrics": False,
                "cache_ttl": 30
            },
            "staging": {
                "debug": False,
                "log_level": "INFO",
                "cors_origins": ["https://staging.senna.com"],
                "feature_stripe_payments": True,
                "enable_metrics": True,
                "cache_ttl": 300
            },
            "production": {
                "debug": False,
                "log_level": "WARNING",
                "cors_origins": ["https://senna.com", "https://app.senna.com"],
                "feature_stripe_payments": True,
                "enable_metrics": True,
                "cache_ttl": 300
            },
        }
        return base_config.get(self.environment, base_config["development"])

    def setup_advanced_logging(self):
        """Setup advanced logging configuration"""
        env_config = self.get_environment_config()

        # Create logs directory if it doesn't exist
        Path("logs").mkdir(exist_ok=True)

        logging_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": self.settings.LOG_FORMAT,
                    "datefmt": "%Y-%m-%d %H:%M:%S"
                },
                "json": {
                    "format": '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "message": "%(message)s"}',
                    "datefmt": "%Y-%m-%d %H:%M:%S"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "level": env_config["log_level"]
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": self.settings.LOG_FILE,
                    "maxBytes": self._parse_size(self.settings.LOG_MAX_SIZE),
                    "backupCount": self.settings.LOG_BACKUP_COUNT,
                    "formatter": "default" if self.is_development() else "json",
                    "level": env_config["log_level"],
                },
                "error_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": "logs/senna_errors.log",
                    "maxBytes": self._parse_size(self.settings.LOG_MAX_SIZE),
                    "backupCount": self.settings.LOG_BACKUP_COUNT,
                    "formatter": "default" if self.is_development() else "json",
                    "level": "ERROR",
                }
            },
            "root": {
                "handlers": ["console", "file", "error_file"] if self.is_production() else ["console", "file"],
                "level": env_config["log_level"]
            },
            "loggers": {
                "senna": {
                    "handlers": ["console", "file"],
                    "level": env_config["log_level"],
                    "propagate": False
                },
                "web3": {
                    "handlers": ["console", "file"],
                    "level": "INFO",
                    "propagate": False
                },
                "ai": {
                    "handlers": ["console", "file"],
                    "level": "INFO",
                    "propagate": False
                }
            }
        }

        logging.config.dictConfig(logging_config)
        logging.info(f"✅ Advanced logging configured for {self.environment} environment")

    def _parse_size(self, size_str: str) -> int:
        """Parse size string like '10MB' to bytes"""
        units = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3}
        number = int(''.join(filter(str.isdigit, size_str)))
        unit = ''.join(filter(str.isalpha, size_str)).upper()
        return number * units.get(unit, 1)

    def get_feature_flags(self) -> Dict[str, bool]:
        """Get all feature flags"""
        return {
            "stripe_payments": self.settings.FEATURE_STRIPE_PAYMENTS,
            "ai_price_recommendations": self.settings.FEATURE_AI_PRICE_RECOMMENDATIONS,
            "smart_contracts": self.settings.FEATURE_SMART_CONTRACTS,
            "portfolio_analytics": self.settings.FEATURE_PORTFOLIO_ANALYTICS,
            "market_predictions": self.settings.FEATURE_MARKET_PREDICTIONS,
            "gas_optimization": self.settings.FEATURE_GAS_OPTIMIZATION,
            "webhooks": self.settings.FEATURE_WEBHOOKS,
            "multi_session": self.settings.FEATURE_MULTI_SESSION,
            "confirmation_flows": self.settings.AI_CONFIRMATION_FLOWS,
            "risk_analysis": self.settings.AI_RISK_ANALYSIS,
            "market_insights": self.settings.AI_MARKET_INSIGHTS,
            "price_prediction": self.settings.AI_PRICE_PREDICTION
        }

    def get_ai_config(self) -> Dict[str, Any]:
        """Get AI configuration"""
        return {
            "provider": self.settings.AI_PROVIDER,
            "model": self.settings.GROQ_MODEL,
            "temperature": self.settings.AI_TEMPERATURE,
            "max_tokens": self.settings.AI_MAX_TOKENS,
            "timeout": self.settings.AI_TIMEOUT,
            "max_context_length": self.settings.AI_MAX_CONTEXT_LENGTH
        }

    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration"""
        return {
            "rate_limit_requests": self.settings.RATE_LIMIT_REQUESTS,
            "rate_limit_window": self.settings.RATE_LIMIT_WINDOW,
            "max_transaction_amount": self.settings.MAX_TRANSACTION_AMOUNT,
            "require_transaction_confirmation": self.settings.REQUIRE_TRANSACTION_CONFIRMATION,
            "session_timeout": self.settings.SESSION_TIMEOUT,
            "jwt_algorithm": self.settings.JWT_ALGORITHM,
            "access_token_expire_minutes": self.settings.ACCESS_TOKEN_EXPIRE_MINUTES
        }

    def get_blockchain_config(self) -> Dict[str, Any]:
        """Get blockchain configuration"""
        return {
            "rpc_url": self.settings.SOMNIA_RPC_URL,
            "chain_id": self.settings.SOMNIA_CHAIN_ID,
            "symbol": self.settings.SOMNIA_SYMBOL,
            "explorer_url": self.settings.SOMNIA_EXPLORER_URL,
            "default_gas_limit": self.settings.DEFAULT_GAS_LIMIT,
            "max_gas_price_gwei": self.settings.MAX_GAS_PRICE_GWEI,
            "transaction_timeout": self.settings.TRANSACTION_TIMEOUT,
            "gas_estimation_buffer": self.settings.GAS_ESTIMATION_BUFFER
        }

    def get_risk_config(self) -> Dict[str, Any]:
        """Get risk management configuration"""
        return {
            "high_amount_threshold": self.settings.RISK_HIGH_AMOUNT_THRESHOLD,
            "new_address_check": self.settings.RISK_NEW_ADDRESS_CHECK,
            "market_volatility_threshold": self.settings.RISK_MARKET_VOLATILITY_THRESHOLD
        }


class AdvancedConfigValidator:
    """Advanced configuration validator for critical settings"""

    @staticmethod
    def validate_blockchain_connection(w3_connection) -> Dict[str, Any]:
        """Validate blockchain connection with detailed diagnostics"""
        try:
            is_connected = w3_connection.is_connected()
            if not is_connected:
                return {"valid": False, "error": "Blockchain connection failed"}
            
            # Additional diagnostics
            block_number = w3_connection.eth.block_number
            gas_price = w3_connection.eth.gas_price
            client_version = w3_connection.client_version
            
            return {
                "valid": True,
                "block_number": block_number,
                "gas_price": gas_price,
                "client_version": client_version,
                "message": "Blockchain connection healthy"
            }
        except Exception as e:
            return {"valid": False, "error": str(e)}

    @staticmethod
    def validate_ai_configuration(settings: AdvancedSettings) -> Dict[str, Any]:
        """Validate AI configuration with provider-specific checks"""
        try:
            if settings.AI_PROVIDER.lower() != "groq":
                return {"valid": False, "error": "Only Groq provider is supported"}
            
            if not settings.GROQ_API_KEY or settings.GROQ_API_KEY.startswith("your_"):
                return {"valid": False, "error": "Groq API key not configured"}
            
            return {
                "valid": True,
                "provider": settings.AI_PROVIDER,
                "model": settings.GROQ_MODEL,
                "message": "AI configuration valid"
            }
        except Exception as e:
            return {"valid": False, "error": str(e)}

    @staticmethod
    def validate_security_settings(settings: AdvancedSettings) -> Dict[str, Any]:
        """Validate security settings comprehensively"""
        warnings = []
        errors = []

        # Critical validations
        if settings.DEBUG and settings.ENVIRONMENT == "production":
            errors.append("DEBUG mode must be disabled in production")

        if len(settings.SECRET_KEY) < 32:
            errors.append("SECRET_KEY must be at least 32 characters")

        if settings.FEATURE_STRIPE_PAYMENTS and not settings.STRIPE_API_KEY:
            warnings.append("Stripe payments enabled but STRIPE_API_KEY not configured")

        # Warning validations
        if settings.CORS_ORIGINS == ["*"] and settings.ENVIRONMENT == "production":
            warnings.append("CORS_ORIGINS is too permissive for production")

        if not settings.REQUIRE_TRANSACTION_CONFIRMATION:
            warnings.append("Transaction confirmation disabled - security risk")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "message": "Security validation completed"
        }

    @staticmethod
    def validate_feature_flags(settings: AdvancedSettings) -> Dict[str, Any]:
        """Validate feature flag dependencies"""
        issues = []

        if settings.FEATURE_AI_PRICE_RECOMMENDATIONS and not settings.GROQ_API_KEY:
            issues.append("AI price recommendations require GROQ_API_KEY")

        if settings.FEATURE_STRIPE_PAYMENTS and not settings.STRIPE_API_KEY:
            issues.append("Stripe payments require STRIPE_API_KEY")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "message": "Feature flag validation completed"
        }


def generate_advanced_env_file(overwrite: bool = False, environment: str = "development"):
    """Generate advanced environment file template"""
    env_file_path = ".env"

    if os.path.exists(env_file_path) and not overwrite:
        logging.info(".env file already exists. Use overwrite=True to regenerate.")
        return

    env_template = f"""# 🧠 Senna Wallet Advanced Environment Configuration
# Sophisticated AI-Powered Wallet Agent for Somnia Blockchain
# Environment: {environment}

# ==================== APPLICATION ====================
DEBUG=true
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT={environment}

# ==================== BLOCKCHAIN ====================
SOMNIA_RPC_URL=https://dream-rpc.somnia.network/
SOMNIA_CHAIN_ID=50312
SOMNIA_SYMBOL=STT
SOMNIA_EXPLORER_URL=https://shannon-explorer.somnia.network/

# ==================== AI CONFIGURATION ====================
AI_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here
GROQ_BASE_URL=https://api.groq.com/openai/v1
GROQ_MODEL=llama-3.1-8b-instant
AI_TEMPERATURE=0.1
AI_MAX_TOKENS=800
AI_MAX_CONTEXT_LENGTH=8000
AI_TIMEOUT=30

# Advanced AI Features
AI_CONFIRMATION_FLOWS=true
AI_RISK_ANALYSIS=true
AI_MARKET_INSIGHTS=true
AI_PRICE_PREDICTION=true

# ==================== SECURITY ====================
SECRET_KEY={secrets.token_urlsafe(64)}
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
SESSION_TIMEOUT=3600
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
MAX_TRANSACTION_AMOUNT=10000.0
REQUIRE_TRANSACTION_CONFIRMATION=true

# ==================== EXTERNAL APIS ====================
STRIPE_API_KEY=your_stripe_api_key_here
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret_here
COINGECKO_API_URL=https://api.coingecko.com/api/v3

# ==================== DATABASE & CACHE ====================
DATABASE_URL=sqlite:///./senna_wallet.db
REDIS_URL=redis://localhost:6379

# ==================== LOGGING ====================
LOG_LEVEL=INFO
LOG_FILE=logs/senna_advanced.log
LOG_MAX_SIZE=10MB
LOG_BACKUP_COUNT=5

# ==================== FEATURE FLAGS ====================
FEATURE_STRIPE_PAYMENTS=false
FEATURE_AI_PRICE_RECOMMENDATIONS=true
FEATURE_SMART_CONTRACTS=false
FEATURE_PORTFOLIO_ANALYTICS=true
FEATURE_MARKET_PREDICTIONS=true
FEATURE_GAS_OPTIMIZATION=true
FEATURE_WEBHOOKS=true
FEATURE_MULTI_SESSION=true

# ==================== TRANSACTION SETTINGS ====================
DEFAULT_GAS_LIMIT=21000
MAX_GAS_PRICE_GWEI=100
TRANSACTION_TIMEOUT=300
GAS_ESTIMATION_BUFFER=1.2

# ==================== CACHE SETTINGS ====================
CACHE_TTL=300
PRICE_CACHE_TTL=60
BALANCE_CACHE_TTL=30

# ==================== CONTRACT ADDRESSES ====================
SOMI_TOKEN_ADDRESS=0xc3DfbBc01Ed164F5f5b4E6B1501B20FfC9B3a49a
SENNA_WALLET_ADDRESS=0x2279aB0dC1AbfCfB1D1cF93360268Fd6C31E8f0E

# ==================== RISK MANAGEMENT ====================
RISK_HIGH_AMOUNT_THRESHOLD=1000.0
RISK_NEW_ADDRESS_CHECK=true
RISK_MARKET_VOLATILITY_THRESHOLD=0.1

# ==================== PERFORMANCE ====================
REQUEST_TIMEOUT=30
MAX_WORKERS=10
BACKGROUND_TASK_INTERVAL=300

# ==================== UI/UX ====================
CHAT_HISTORY_LIMIT=100
AUTO_COMPLETE_SUGGESTIONS=true
TRANSACTION_PREVIEWS=true
MARKET_ALERTS=true

# ==================== MONITORING ====================
ENABLE_METRICS=true
METRICS_PORT=9090
HEALTH_CHECK_INTERVAL=30

# ==================== CORS ====================
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:8080,http://127.0.0.1:8080
"""

    with open(env_file_path, "w") as f:
        f.write(env_template)

    logging.info(f"✅ Advanced environment template generated at {env_file_path} for {environment} environment")


def get_advanced_config_summary() -> Dict[str, Any]:
    """Get comprehensive configuration summary"""
    env_manager = AdvancedEnvironmentManager()
    
    return {
        "application": {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG
        },
        "api": {
            "host": settings.API_HOST,
            "port": settings.API_PORT,
            "cors_origins": settings.CORS_ORIGINS
        },
        "blockchain": {
            "network": "Somnia Testnet",
            "chain_id": settings.SOMNIA_CHAIN_ID,
            "symbol": settings.SOMNIA_SYMBOL,
            "connected": "Unknown"  # Would be checked at runtime
        },
        "ai": env_manager.get_ai_config(),
        "features": env_manager.get_feature_flags(),
        "security": env_manager.get_security_config(),
        "risk_management": env_manager.get_risk_config(),
        "performance": {
            "cache_ttl": settings.CACHE_TTL,
            "request_timeout": settings.REQUEST_TIMEOUT,
            "max_workers": settings.MAX_WORKERS
        }
    }


# Initialize advanced environment manager
env_manager = AdvancedEnvironmentManager()

# Export public interface
__all__ = [
    "settings",
    "get_settings", 
    "env_manager",
    "generate_advanced_env_file",
    "get_advanced_config_summary",
    "AdvancedConfigValidator"
]