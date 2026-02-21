"""
MartletMolt 主入口點
"""

from martlet_molt.gateway.server import app, create_app, run_server

__all__ = ["app", "create_app", "run_server"]


if __name__ == "__main__":
    run_server()
