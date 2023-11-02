import time
from watchdog.observers import Observer
from models.handler import Handler


class Watcher:
    directory_to_watch = None
    driver = None

    def __init__(self, **config):
        self.observer = Observer()
        self.directory_to_watch = config['path']
        self.driver = config['driver']

    def run(self):
        print("Directory watch running..")

        event_handler = Handler(driver=self.driver)
        self.observer.schedule(
            event_handler, self.directory_to_watch, recursive=True)
        self.observer.start()

        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Directory watch stopped.")

        self.observer.join()
