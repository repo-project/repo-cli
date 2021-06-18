import pexpect
import pytest


def test_test():
    cli = pexpect.spawn("repo-cli", timeout=1)
    cli.close()
