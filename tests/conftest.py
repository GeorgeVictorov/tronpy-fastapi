import pytest


def pytest_configure(config):
    config.option.asyncio_default_fixture_loop_scope = "function"
