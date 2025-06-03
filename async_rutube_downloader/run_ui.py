import asyncio
from asyncio import AbstractEventLoop
from threading import Thread

from async_rutube_downloader.downloader import Downloader
from async_rutube_downloader.ui import DownloaderUI


class ThreadedEventLoop(Thread):
    """We create a new thread class
    to run the asyncio event loop forever inside."""

    def __init__(self, loop: AbstractEventLoop) -> None:
        super().__init__()
        self._loop = loop
        self.daemon = True
        """We set the thread to be daemon
        because the asyncio event loop will block
        and run forever in this thread."""

    def run(self) -> None:
        """
        There is no target for the thread to run(like Thread(target=foo)),
        so we override the run method.
        So, on start, the thread will run the event loop forever.
        """
        self._loop.run_forever()


def main() -> None:
    loop = asyncio.new_event_loop()

    asyncio_thread = ThreadedEventLoop(loop)
    asyncio_thread.start()
    """
    Start the new thread to run the asyncio event loop in the background.
    """

    app = DownloaderUI(
        downloader_class=Downloader,
        loop=loop,
    )
    """
    Create the Tkinter application, and start its main event loop.
    """
    app.mainloop()


if __name__ == "__main__":
    main()
