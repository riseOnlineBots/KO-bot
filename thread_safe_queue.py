import threading


class ThreadSafeQueue:
    def __init__(self):
        self.mutex = threading.Lock()
        self.queue = []
        self.event = threading.Event()

    def clear(self):
        self.queue = []
        self.event.clear()

    def put(self, data):
        with self.mutex:
            self.queue.append(data)
            self.event.set()

    def get(self):
        self.event.wait()
        with self.mutex:
            if self.queue:
                return self.queue.pop()
            else:
                return None
