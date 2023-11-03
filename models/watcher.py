import time

from watchdog.observers import Observer

from models.handler import Handler


class Watcher:
    directory_to_watch = None
    driver = None

    def __init__(self, **config):
        self.observer = Observer()
        self.directory_to_watch = config["path"]
        self.driver = config["driver"]

    def run(self):
        print("Press CTRL+C to exit.")
        print("Listen to directory: {}".format(self.directory_to_watch))

        event_handler = Handler(driver=self.driver)
        self.observer.schedule(event_handler, self.directory_to_watch, recursive=False)
        self.observer.start()

        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            self.observer.stop()
            print("Listening to {} stopped".format(self.directory_to_watch))
        except Exception as e:
            print(e)

        self.observer.join()
