"""Thread pool worker implementation."""

import os
import queue
import threading


class Worker:
    """Background worker that processes tasks in a thread pool."""

    def __init__(self, task_queue: queue.Queue, gui_opened: bool) -> None:
        """Initialize the worker pool."""
        self.task_queue = task_queue
        self.gui_opened = gui_opened
        self.threads_count = os.cpu_count() or 4
        self.threads: list[threading.Thread] = []
        self.start_workers()

    def start_workers(self) -> None:
        """Start worker threads."""
        for _ in range(self.threads_count):
            thread = threading.Thread(target=self.worker, daemon=True)
            thread.start()
            self.threads.append(thread)

    def worker(self) -> None:
        """Process tasks until the GUI closes."""
        while self.gui_opened:
            try:
                func, args = self.task_queue.get(timeout=1)
                func(*args)
                self.task_queue.task_done()
            except queue.Empty:
                continue

    def stop_workers(self, gui_opened: bool) -> None:
        """Signal all worker threads to stop."""
        self.gui_opened = gui_opened
        for thread in self.threads:
            thread.join(timeout=1)
