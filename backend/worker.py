import threading, queue, os

class Worker:
    def __init__(self, task_queue, gui_opened):
        self.task_queue = task_queue
        self.gui_opened = gui_opened
        self.threads_count = os.cpu_count() or 4  # Number of threads
        self.threads = []
        self.start_workers()

    def start_workers(self):
        for _ in range(self.threads_count):
            thread = threading.Thread(target=self.worker, daemon=True)  # Set daemon=True to terminate on exit
            thread.start()
            self.threads.append(thread)

    def worker(self):
        while self.gui_opened:  # Check stop event
            try:
                func, args = self.task_queue.get(timeout=1)
                func(*args)
                self.task_queue.task_done()
            except queue.Empty:
                continue  # Avoid busy-waiting

    def stop_workers(self, gui_opened):
        """Signal all worker threads to stop."""
        self.gui_opened = gui_opened # Signal threads to stop
        for thread in self.threads:
            thread.join(timeout=1)  # Allow threads to exit gracefully