import threading, queue

class Worker:
    def __init__(self, task_queue, gui_opened):
        self.task_queue = task_queue
        self.gui_opened = gui_opened
        self.start_workers()

    def start_workers(self):
        for _ in range(4):  # You can adjust the number of threads
            threading.Thread(target=self.worker).start()

    def worker(self):
        while self.gui_opened:
            try:
                func, args = self.task_queue.get(timeout=1)
                func(*args)
                self.task_queue.task_done()
            except queue.Empty:
                continue
