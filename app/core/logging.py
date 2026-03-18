import logging


def configure_logging(debug: bool = True) -> None:
    """为本地开发配置根日志器。"""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
