import sys
from argparse import Namespace, RawDescriptionHelpFormatter
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from async_rutube_downloader.run_cli import (
    CLI_DESCRIPTION,
    CLI_EPILOG,
    CLI_NAME,
    REPORT_MULTIPLE_URLS,
    WIDTH_OF_PROGRESS_BAR,
    CLIDownloader,
    create_parser,
    create_progress_bar,
    parse_args,
)
from async_rutube_downloader.run_cli import main as cli_main
from async_rutube_downloader.settings import (
    AVAILABLE_QUALITIES,
    DOWNLOAD_DIR,
    SELECT_QUALITY,
    FULL_HD_1080p,
    HD_720p,
)
from tests.conftest import RUTUBE_ID


def test_create_progress_bar() -> None:
    progress_bar = create_progress_bar()
    assert len(progress_bar) == WIDTH_OF_PROGRESS_BAR
    assert all(char == " " for char in progress_bar)


def test_create_parser() -> None:
    parser = create_parser()
    assert parser.description == CLI_DESCRIPTION
    assert parser.prog == CLI_NAME
    assert parser.epilog == CLI_EPILOG
    assert parser.formatter_class == RawDescriptionHelpFormatter


@pytest.mark.parametrize(
    "url, optional_arg",
    (
        (f"https://rutube.ru/video/{RUTUBE_ID}/", []),
        (RUTUBE_ID, []),
        (RUTUBE_ID, ["-q"]),
        (RUTUBE_ID, ["-o", str(Path.cwd())]),
        (RUTUBE_ID, ["-d", ";"]),
        (RUTUBE_ID, ["-f", "./path/to/file"]),
        (RUTUBE_ID, ["-f", "./path/to/file", "-q"]),
        (RUTUBE_ID, ["-f", "./path/to/file", "-d", ";"]),
        (RUTUBE_ID, ["-f", "./path/to/file", "-d", ";", "-q"]),
        (
            RUTUBE_ID,
            ["-f", "./path/to/file", "-d", ";", "-q", "-o", str(Path.cwd())],
        ),
    ),
)
def test_parse_args(
    url: str, optional_arg: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    test_args = ["async_rutube_downloader"]
    if url:
        test_args.append(url)
    if optional_arg:
        test_args.extend(optional_arg)
    monkeypatch.setattr("sys.argv", test_args)  # Mock sys.argv

    parser = create_parser()
    cli_args = parse_args(parser)
    assert isinstance(cli_args, Namespace)
    assert cli_args.url == url
    assert cli_args.output == Path.cwd()
    assert cli_args.quality is ("-q" in optional_arg)
    assert (
        cli_args.file is None
        if "-f" not in optional_arg
        else optional_arg[optional_arg.index("-f") + 1]
    )
    assert (
        cli_args.delimiter == "\n"
        if "-d" not in optional_arg
        else optional_arg[optional_arg.index("-d") + 1]
    )


def test_invalid_directory_shows_error_message(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    invalid_path = "fake/path/to/folder"
    test_args = [
        "async_rutube_downloader",
        RUTUBE_ID,
        "-o",
        invalid_path,
    ]
    monkeypatch.setattr("sys.argv", test_args)
    with pytest.raises(SystemExit):
        cli_main()
    captured = capsys.readouterr()
    assert captured.out == ""
    assert invalid_path in captured.err


@patch(
    "async_rutube_downloader.run_cli.CLIDownloader.download_single_video",
    autospec=True,
)
def test_cli_download_single_url(
    mocked_method: AsyncMock,
    cli_single_url_fixture: None,
) -> None:
    cli_main()
    mocked_method.assert_called_once()


@patch(
    "async_rutube_downloader.run_cli.CLIDownloader.download_single_video",
    autospec=True,
)
def test_cli_download_from_file(
    mocked_method: AsyncMock,
    cli_file_fixture: None,
    capsys: pytest.CaptureFixture[str],
) -> None:
    urls_in_fixture = 3
    cli_main()
    assert mocked_method.call_count == urls_in_fixture
    captured = capsys.readouterr()
    assert (
        captured.out == f"{DOWNLOAD_DIR.format(Path.cwd())}\n"
        f"{REPORT_MULTIPLE_URLS.format(urls_in_fixture, 0, 0, 0)}\n"
    )
    assert captured.err == ""


@pytest.mark.parametrize(
    "entry_point",
    [
        "rtube-cli",
        ["python", "-m", "async_rutube_downloader"],
        ["python", "async_rutube_downloader/run_cli.py"],
    ],
)
def test_cli_entry_points(entry_point: str) -> None:
    import subprocess

    result = subprocess.run(entry_point, stdout=subprocess.DEVNULL)
    result.check_returncode()


@patch.object(
    sys,
    "argv",
    ["async_rutube_downloader", "-h"],
)
def test_cli_help_text(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit):
        cli_main()

    captured = capsys.readouterr()
    assert CLI_NAME in captured.out
    assert CLI_EPILOG in captured.out
    assert CLI_DESCRIPTION in captured.out
    assert "-h" and "--help" in captured.out
    assert "-q" and "--quality" in captured.out
    assert "-o" and "--output" in captured.out
    assert "-f" and "--file" in captured.out
    assert "-d" and "--delimiter" in captured.out
    assert captured.err == ""


def test_print_progress_bar(
    capsys: pytest.CaptureFixture[str], cli_downloader: CLIDownloader
) -> None:
    progress_bar = create_progress_bar()
    progress_bar[0] = "#"
    # 1
    cli_downloader._print_progress_bar(progress_bar)
    captured = capsys.readouterr()
    assert captured.out == f"\r[#{' ' * 19}]"
    assert captured.err == ""
    # 2
    cli_downloader._print_progress_bar(progress_bar, last=True)
    captured = capsys.readouterr()
    assert captured.out == f"\r[#{' ' * 19}]\n"
    assert captured.err == ""


def test_ask_for_quality(
    capsys: pytest.CaptureFixture[str],
    cli_downloader: CLIDownloader,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("builtins.input", lambda: "1")
    qualities = FULL_HD_1080p, HD_720p
    cli_downloader.ask_for_quality(qualities)
    captured = capsys.readouterr()
    expected_output = f"""{AVAILABLE_QUALITIES}
1. {"x".join(str(i) for i in FULL_HD_1080p)}
2. {"x".join(str(i) for i in HD_720p)}
{SELECT_QUALITY}
"""
    assert captured.out == expected_output
    assert captured.err == ""


@patch(
    "async_rutube_downloader.run_cli.CLIDownloader._print_progress_bar",
    autospec=True,
)
@pytest.mark.parametrize(
    "completed_chunks, total_chunks, is_end",
    ((1, 16, False), (16, 16, True)),
)
@pytest.mark.asyncio
async def test_cli_progress_callback(
    mocked_print_func: MagicMock,
    cli_downloader: CLIDownloader,
    completed_chunks: int,
    total_chunks: int,
    is_end: bool,
) -> None:
    await cli_downloader._cli_progress_callback(completed_chunks, total_chunks)
    mocked_print_func.assert_called_once_with(
        cli_downloader, cli_downloader.progress_bar, is_end
    )
