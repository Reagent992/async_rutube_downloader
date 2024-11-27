import asyncio
from asyncio import AbstractEventLoop
from threading import Thread

from ui import DownloaderUI


class ThreadedEventLoop(Thread):
    """We create a new thread class
    to run the asyncio event loop forever inside."""

    def __init__(self, loop: AbstractEventLoop):
        super().__init__()
        self._loop = loop
        self.daemon = True
        """We set the thread to be daemon
        because the asyncio event loop will block
        and run forever in this thread."""

    def run(self):
        self._loop.run_forever()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()

    asyncio_thread = ThreadedEventLoop(loop)
    asyncio_thread.start()
    """
    Start the new thread to run the asyncio event loop in the background.
    """

    app = DownloaderUI(loop)
    """
    Create the load tester Tkinter application, and start its main event loop.
    """
    app.mainloop()
