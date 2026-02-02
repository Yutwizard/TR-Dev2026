"""
Treasury Management System - Configuration Settings
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # ==========================================================================
    # Application
    # ==========================================================================
    APP_NAME: str = "Treasury Management System"
    APP_ENV: str = Field(default="development", description="development, staging, production")
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    
    # ==========================================================================
    # API
    # ==========================================================================
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    
    # ==========================================================================
    # Database
    # ==========================================================================
    DATABASE_URL: str = Field(
        default="postgresql://tms_user:tms_password@localhost:5432/treasury_local",
        description="PostgreSQL connection string"
    )
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE: int = 3600
    
    # ==========================================================================
    # Redis
    # ==========================================================================
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600
    
    # ==========================================================================
    # Security & Authentication
    # ==========================================================================
    SECRET_KEY: str = Field(
        default="your-super-secret-key-change-in-production",
        description="Secret key for JWT signing. Generate with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Password policy
    PASSWORD_MIN_LENGTH: int = 8
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 30
    
    # ==========================================================================
    # CORS
    # ==========================================================================
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="Allowed CORS origins"
    )
    
    # ==========================================================================
    # Data Paths
    # ==========================================================================
    EXCEL_DATA_PATH: str = "../../data/source/Treasury_System_Database_V2_Internal.xlsx"
    OUTPUT_PATH: str = "../../output/"
    BAHTNET_OUTPUT_PATH: str = "../../output/bahtnet/"
    TSD_OUTPUT_PATH: str = "../../output/tsd/"
    
    # ==========================================================================
    # External Integrations
    # ==========================================================================
    # ThaiBMA
    THAIBMA_API_URL: str = "https://api.thaibma.or.th"
    THAIBMA_API_KEY: str = ""
    THAIBMA_ENABLED: bool = False
    
    # BOT API
    BOT_API_URL: str = "https://apigw1.bot.or.th/bot/public"
    BOT_API_KEY: str = ""
    BOT_API_ENABLED: bool = False
    
    # ==========================================================================
    # Settlement Systems (Manual Mode)
    # ==========================================================================
    BAHTNET_MODE: str = "manual"  # 'manual' or 'api'
    BAHTNET_BANK_CODE: str = ""
    
    TSD_MODE: str = "manual"
    TSD_PARTICIPANT_CODE: str = ""
    
    # ==========================================================================
    # Business Rules
    # ==========================================================================
    SETTLEMENT_CYCLE_DAYS: int = 2  # T+2
    LIMIT_WARNING_THRESHOLD: int = 80  # Warn at 80% utilization
    LIMIT_BLOCK_THRESHOLD: int = 100   # Block at 100%
    THAIBMA_REPORT_DEADLINE_MINUTES: int = 30
    
    # ==========================================================================
    # Batch Processing
    # ==========================================================================
    EOD_BATCH_TIME: str = "18:00"
    ACCRUAL_CALCULATION_TIME: str = "17:30"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Singleton instance
settings = get_settings()
