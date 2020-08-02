#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `stwberlin_menus.cli` package."""

import typing

import pytest
from click.testing import CliRunner

from stwberlin_menus import cli, stwberlin_menus

def test_parse_dates() -> None:
    assert cli._parse_dates()


def test_command_line_interface() -> None:
    """Test the CLI.
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert "stwberlin_menus.cli.main" in result.output
    help_result = runner.invoke(cli.main, ["--help"])
    assert help_result.exit_code == 0
    assert "--help  Show this message and exit." in help_result.output
    """
    pass
