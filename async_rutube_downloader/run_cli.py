import asyncio
import signal
import time
from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter
from pathlib import Path

import aiofiles
from aiohttp import ClientSession

from async_rutube_downloader.downloader import Downloader
from async_rutube_downloader.settings import (
    API_RESPONSE_ERROR_MSG,
    AVAILABLE_QUALITIES,
    CLI_DESCRIPTION,
    CLI_EPILOG,
    CLI_NAME,
    DOWNLOAD_CANCELED,
    FILE_NOT_FOUND_ERROR_MSG,
    INVALID_FILE_ERROR_MSG,
    INVALID_URL,
    PATH_IS_A_DIRECTORY_ERROR_MSG,
    REPORT_MULTIPLE_URLS,
    SELECT_QUALITY,
    _,
)
from async_rutube_downloader.ui import SEGMENT_DOWNLOAD_ERROR_MSG
from async_rutube_downloader.utils.create_session import create_aiohttp_session
from async_rutube_downloader.utils.exceptions import (
    APIResponseError,
    CLIFileError,
    InvalidURLError,
    SegmentDownloadError,
)
from async_rutube_downloader.utils.logger import get_logger
from async_rutube_downloader.utils.miscellaneous import (
    get_or_create_loop,
    get_version_from_pyproject,
)
from async_rutube_downloader.utils.type_hints import Qualities
from async_rutube_downloader.utils.validators import (
    cli_quality_validator,
    cli_validate_path,
    cli_validate_urls_file,
)

logger = get_logger(__name__)
INDEX_OFFSET = 1
WIDTH_OF_PROGRESS_BAR = 20
PROGRESS_BAR_STEP_PERCENT = 5


def create_progress_bar() -> list[str]:
    return [*[" " for _ in range(WIDTH_OF_PROGRESS_BAR)]]


class CLIDownloader:
    def __init__(
        self,
        cli_args: Namespace,
        session: ClientSession,
        event_loop: asyncio.AbstractEventLoop | None = None,
    ) -> None:
        self.cli_args = cli_args
        self.event_loop = event_loop if event_loop else get_or_create_loop()
        self.session = session
        self.progress_bar = create_progress_bar()
        self.downloader: Downloader | None = None
        self.__last_step: int = 0
        self.__download_cancelled = False
        self.__tasks: list[asyncio.Task] = []

    def cli_progress_callback(
        self,
        completed_chunks: int,
        total_chunks: int,
    ) -> None:
        self.__tasks.append(
            asyncio.create_task(
                self._cli_progress_callback(completed_chunks, total_chunks)
            )
        )

    async def _cli_progress_callback(
        self, completed_chunks, total_chunks
    ) -> None:
        completion_percentage = int((completed_chunks / total_chunks) * 100)
        progress_step = completion_percentage // PROGRESS_BAR_STEP_PERCENT
        if progress_step > self.__last_step:
            self.progress_bar[self.__last_step : progress_step] = "#" * (
                progress_step - self.__last_step
            )
            self.__last_step = progress_step
            self._print_progress_bar(
                self.progress_bar,
                True if completion_percentage == 100 else False,
            )

    def _print_progress_bar(
        self, progress_bar: list[str], last: bool = False
    ) -> None:
        print(
            f"\r[{''.join(progress_bar)}]",
            end="" if not last else "\n",
            flush=True,
        )

    def ask_for_quality(self, qualities: Qualities) -> tuple[int, int]:
        available_qualities = {}
        print(AVAILABLE_QUALITIES)
        for index, quality in enumerate(qualities):
            print(
                f"{index + INDEX_OFFSET}. {'x'.join(str(i) for i in quality)}"
            )
            available_qualities[index + INDEX_OFFSET] = quality
        user_input = None
        while cli_quality_validator(user_input, available_qualities) is False:
            print(SELECT_QUALITY)
            user_input = input()
        return available_qualities[int(user_input)]  # type: ignore

    def _print_state(self) -> None:
        assert self.downloader
        if not self.downloader.is_interrupted():
            minutes, seconds = divmod(self._download_time, 60)
            print(
                _("[{}] downloaded in {} minutes, {} seconds").format(
                    self.downloader.video_title, minutes, seconds
                )
            )
            print(
                _("[{}] saved to {}").format(
                    self.downloader.video_title, self.downloader.file
                )
            )
        else:
            print(DOWNLOAD_CANCELED)

    async def download_single_video(
        self,
        url: str = "",
    ) -> None:
        start_time = time.time()
        self.__current_download = self._download_single_video(url)
        await self.__current_download
        end_time = time.time()
        self._download_time = round(end_time - start_time)
        self._print_state()

    async def _download_single_video(self, url) -> None:
        self.downloader = Downloader(
            url if url else self.cli_args.url,
            loop=self.event_loop,
            callback=self.cli_progress_callback,
            upload_directory=self.cli_args.output,
            session=self.session,
            auto_close_session=False if url else True,
        )
        qualities = await self.downloader.fetch_video_info()
        if self.cli_args.quality:
            selected_quality = self.ask_for_quality(qualities)
            await self.downloader.select_quality(selected_quality)
        print(_("[{}] download started").format(self.downloader.video_title))
        await self.downloader.download_video()
        await asyncio.gather(*self.__tasks)

    def interrupt_download(self) -> None:
        # FIXME: add interrupt while selecting qualities.
        if self.downloader:
            self.downloader.interrupt_download()
            self.__download_cancelled = True

    async def get_urls_list_from_file(
        self, user_file: Path, delimiter: str
    ) -> list[str]:
        async with aiofiles.open(user_file) as file:
            raw_result = await file.read()
            result = raw_result.strip().split(delimiter)
            return result

    async def download_multiple_videos(self, cli_args: Namespace) -> None:
        start_time = time.time()
        success_downloads, invalid_urls = await self._download_multiple_videos(
            cli_args
        )
        end_time = time.time()
        if not self.__download_cancelled:
            total_seconds = round(end_time - start_time)
            minutes, seconds = divmod(total_seconds, 60)
            print(
                REPORT_MULTIPLE_URLS.format(
                    success_downloads, invalid_urls, minutes, seconds
                )
            )

    async def _download_multiple_videos(self, cli_args) -> tuple[int, int]:
        success_downloads = 0
        invalid_urls = 0
        urls = await self.get_urls_list_from_file(
            cli_args.file, cli_args.delimiter
        )
        if not cli_validate_urls_file(urls):
            raise CLIFileError
        for url in urls:
            if self.__download_cancelled:
                break

            try:
                # cleanup
                self.progress_bar = create_progress_bar()
                self.__last_step = 0
                self.__tasks = []

                await self.download_single_video(url)
                success_downloads += 1
            except InvalidURLError:
                print(_("Invalid URL Error: {}").format(url))
                invalid_urls += 1
                continue
        return success_downloads, invalid_urls


def parse_args(parser: ArgumentParser) -> Namespace:
    # I think cli looks better when metavar=""
    parser.add_argument(
        "url",
        nargs="?",
        default=None,
        help=_("URL or ID of the Rutube video"),
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="",
        type=cli_validate_path,
        default=Path.cwd(),
        help=_("Output directory (default: current working directory)"),
    )
    parser.add_argument(
        "-q",
        "--quality",
        action="store_true",
        help=_("Select video quality interactively"),
    )
    parser_multiple_videos_group = parser.add_argument_group(
        _("Multiple videos download")
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=get_version_from_pyproject(),
    )
    parser_multiple_videos_group.add_argument(
        "-f",
        "--file",
        metavar="",
        type=Path,
        help=_("Path to the file with URLs"),
    )
    parser_multiple_videos_group.add_argument(
        "-d",
        "--delimiter",
        metavar="",
        type=str,
        help=_("Delimiter between URLs in the file(default: \\n)"),
        default="\n",
    )
    return parser.parse_args()


def create_parser() -> ArgumentParser:
    return ArgumentParser(
        prog=CLI_NAME,
        description=CLI_DESCRIPTION,
        epilog=CLI_EPILOG,
        formatter_class=RawDescriptionHelpFormatter,
    )


def _interrupt_and_report(cli_downloader: CLIDownloader) -> None:
    print("\n", _("Cancelling download..."))
    cli_downloader.interrupt_download()


def handle_exception(msg: str, *args):
    if args:
        msg = msg.format(*args)
    print(msg)
    logger.info(msg, exc_info=True)


def main(
    event_loop: asyncio.AbstractEventLoop | None = None,
    session: ClientSession | None = None,
) -> None:
    # Manually handling the eventloop, to do a Graceful Shutdowns.
    parser = create_parser()
    cli_args = parse_args(parser)
    if not event_loop:
        event_loop = asyncio.new_event_loop()
    if not session:
        session = create_aiohttp_session(event_loop)
    cli_downloader = CLIDownloader(cli_args, session, event_loop)

    try:
        event_loop.add_signal_handler(
            signal.SIGINT, lambda: _interrupt_and_report(cli_downloader)
        )
        if cli_args.url:
            print(_("Download directory: {}").format(cli_args.output))
            event_loop.run_until_complete(
                cli_downloader.download_single_video()
            )
        elif cli_args.file:
            print(_("Download directory: {}").format(cli_args.output))
            event_loop.run_until_complete(
                cli_downloader.download_multiple_videos(cli_args)
            )
        else:
            parser.print_help()
    except APIResponseError:
        handle_exception(API_RESPONSE_ERROR_MSG)
    except InvalidURLError:
        handle_exception(INVALID_URL)
    except SegmentDownloadError:
        handle_exception(SEGMENT_DOWNLOAD_ERROR_MSG)
    except FileNotFoundError:
        handle_exception(FILE_NOT_FOUND_ERROR_MSG, cli_args.file)
    except IsADirectoryError:
        handle_exception(PATH_IS_A_DIRECTORY_ERROR_MSG, cli_args.file)
    except CLIFileError:
        handle_exception(INVALID_FILE_ERROR_MSG)
    finally:
        event_loop.run_until_complete(session.close())
        event_loop.close()


if __name__ == "__main__":
    main()
