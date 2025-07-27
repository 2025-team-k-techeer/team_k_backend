import logging
import sys
from typing import Optional


def setup_logger(
    name: str = "team_k_backend",
    level: str = "INFO",
    log_format: Optional[str] = None,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """
    애플리케이션 로거 설정

    Args:
        name: 로거 이름
        level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: 로그 포맷 문자열
        log_file: 로그 파일 경로 (선택사항)

    Returns:
        설정된 로거 인스턴스
    """
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # 로거 생성
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # 이미 핸들러가 설정되어 있다면 중복 방지
    if logger.handlers:
        return logger

    # 콘솔 핸들러 설정
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))

    # 포맷터 설정
    formatter = logging.Formatter(log_format)
    console_handler.setFormatter(formatter)

    # 핸들러 추가
    logger.addHandler(console_handler)

    # 파일 핸들러 설정 (선택사항)
    if log_file:
        try:
            # 로그 디렉토리 생성
            import os

            os.makedirs(os.path.dirname(log_file), exist_ok=True)

            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(getattr(logging, level.upper()))
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            # 파일 핸들러 생성 실패 시 콘솔에만 로그
            print(f"로그 파일 핸들러 생성 실패: {e}")

    return logger


def get_logger(name: str = "team_k_backend") -> logging.Logger:
    """
    기존 로거 가져오기 또는 새로 생성

    Args:
        name: 로거 이름

    Returns:
        로거 인스턴스
    """
    return logging.getLogger(name)
