from argparse import Namespace, RawDescriptionHelpFormatter
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from async_rutube_downloader.run_cli import (
    CLI_DESCRIPTION,
    CLI_EPILOG,
    CLI_NAME,
    DOWNLOAD_DIR,
    REPORT_MULTIPLE_URLS,
    WIDTH_OF_PROGRESS_BAR,
    create_parser,
    create_progress_bar,
    parse_args,
)
from async_rutube_downloader.run_cli import main as cli_main


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
    "url,optional_arg",
    [
        ("https://rutube.ru/video/365ae8f40a2ffd2a5901ace4db799de7/", []),
        ("365ae8f40a2ffd2a5901ace4db799de7", []),
        ("365ae8f40a2ffd2a5901ace4db799de7", ["-q"]),
        ("365ae8f40a2ffd2a5901ace4db799de7", ["-o", str(Path.cwd())]),
        ("365ae8f40a2ffd2a5901ace4db799de7", ["-d", ";"]),
        ("365ae8f40a2ffd2a5901ace4db799de7", ["-f", "./path/to/file"]),
        ("365ae8f40a2ffd2a5901ace4db799de7", ["-f", "./path/to/file", "-q"]),
        (
            "365ae8f40a2ffd2a5901ace4db799de7",
            ["-f", "./path/to/file", "-d", ";"],
        ),
        (
            "365ae8f40a2ffd2a5901ace4db799de7",
            ["-f", "./path/to/file", "-d", ";", "-q"],
        ),
        (
            "365ae8f40a2ffd2a5901ace4db799de7",
            ["-f", "./path/to/file", "-d", ";", "-q", "-o", str(Path.cwd())],
        ),
    ],
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
        "365ae8f40a2ffd2a5901ace4db799de7",
        "-o",
        invalid_path,
    ]
    monkeypatch.setattr("sys.argv", test_args)
    with pytest.raises(SystemExit):
        cli_main()
    captured = capsys.readouterr()
    assert captured.out == ""
    assert invalid_path in captured.err


def test_cli_download_single_url(
    cli_single_url_fixture: None, mocker: MockerFixture
) -> None:
    mock_method = mocker.patch(
        "async_rutube_downloader.run_cli.CLIDownloader.download_single_video"
    )
    cli_main()
    mock_method.assert_called_once()


def test_cli_download_from_file(
    cli_file_fixture: None,
    mocker: MockerFixture,
    capsys: pytest.CaptureFixture[str],
) -> None:
    mock_method = mocker.patch(
        "async_rutube_downloader.run_cli.CLIDownloader.download_single_video"
    )
    cli_main()
    assert mock_method.call_count == 3
    captured = capsys.readouterr()
    assert (
        captured.out == f"{DOWNLOAD_DIR.format(Path.cwd())}\n"
        f"{REPORT_MULTIPLE_URLS.format(3, 0, 0, 0)}\n"
    )
    assert captured.err == ""


@pytest.mark.parametrize(
    "entry_point",
    [
        "run_cli",
        ["python", "-m", "async_rutube_downloader"],
        ["python", "async_rutube_downloader/run_cli.py"],
    ],
)
def test_cli_entry_points(entry_point: str) -> None:
    import subprocess

    result = subprocess.run(entry_point, stdout=subprocess.DEVNULL)
    result.check_returncode()


def test_cli_help_text(
    capsys: pytest.CaptureFixture[str], mocker: MockerFixture
) -> None:
    test_args = ["async_rutube_downloader", "-h"]
    mocker.patch("sys.argv", test_args)

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
