class EventQueue(object):
    def __init__(self, start_event):
        self.queue = []
        self.current_event = start_event
        self.push(start_event)

    def pop(self):
        self.queue.pop(0)
        if not len(self.queue):
            self.current_event = None
            return
        self.current_event = self.queue[0]

    def push(self, event):
<<<<<<< HEAD
        self.queue.append(event)
=======
        self.queue.append(event)
>>>>>>> fb78d41550d471ef727838696ff62068320965e6
