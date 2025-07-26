#!/usr/bin/env python3
"""
로그 뷰어 스크립트
Docker 컨테이너의 로그를 실시간으로 확인할 수 있습니다.
"""

import subprocess
import sys
import argparse
from typing import Optional


def follow_logs(container_name: str, lines: int = 100, service: Optional[str] = None):
    """
    Docker 컨테이너의 로그를 실시간으로 추적

    Args:
        container_name: 컨테이너 이름
        lines: 처음에 보여줄 로그 라인 수
        service: docker-compose 서비스 이름 (선택사항)
    """
    try:
        if service:
            # docker-compose를 사용하는 경우
            cmd = [
                "docker-compose",
                "-f",
                "dev-docker-compose.yml",
                "logs",
                "-f",
                "--tail",
                str(lines),
                service,
            ]
        else:
            # 직접 컨테이너에 접근하는 경우
            cmd = ["docker", "logs", "-f", "--tail", str(lines), container_name]

        print(f"🔍 로그 추적 시작: {' '.join(cmd)}")
        print("=" * 80)

        # 실시간 로그 출력
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
        )

        for line in process.stdout:
            print(line.rstrip())

    except KeyboardInterrupt:
        print("\n⏹️  로그 추적을 중단했습니다.")
    except subprocess.CalledProcessError as e:
        print(f"❌ 오류 발생: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Docker가 설치되지 않았거나 PATH에 없습니다.")
        sys.exit(1)


def show_recent_logs(
    container_name: str, lines: int = 50, service: Optional[str] = None
):
    """
    최근 로그만 보기

    Args:
        container_name: 컨테이너 이름
        lines: 보여줄 로그 라인 수
        service: docker-compose 서비스 이름 (선택사항)
    """
    try:
        if service:
            cmd = [
                "docker-compose",
                "-f",
                "dev-docker-compose.yml",
                "logs",
                "--tail",
                str(lines),
                service,
            ]
        else:
            cmd = ["docker", "logs", "--tail", str(lines), container_name]

        print(f"📋 최근 로그 ({lines}줄): {' '.join(cmd)}")
        print("=" * 80)

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"❌ 오류: {result.stderr}")

    except subprocess.CalledProcessError as e:
        print(f"❌ 오류 발생: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Docker가 설치되지 않았거나 PATH에 없습니다.")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Docker 로그 뷰어")
    parser.add_argument(
        "--container", "-c", default="fastapi", help="컨테이너 이름 (기본값: fastapi)"
    )
    parser.add_argument("--service", "-s", help="docker-compose 서비스 이름 (선택사항)")
    parser.add_argument(
        "--lines",
        "-n",
        type=int,
        default=100,
        help="처음에 보여줄 로그 라인 수 (기본값: 100)",
    )
    parser.add_argument(
        "--follow",
        "-f",
        action="store_true",
        help="실시간 로그 추적 (기본값: 최근 로그만)",
    )

    args = parser.parse_args()

    if args.follow:
        follow_logs(args.container, args.lines, args.service)
    else:
        show_recent_logs(args.container, args.lines, args.service)


if __name__ == "__main__":
    main()
