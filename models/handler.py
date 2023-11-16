import os
import time

import watchdog.events


class Handler(watchdog.events.PatternMatchingEventHandler):
    driver = None

    def __init__(self, **kwargs):
        watchdog.events.PatternMatchingEventHandler.__init__(
            self, patterns=["*.xlsx"], ignore_directories=True, case_sensitive=False
        )
        self.driver = kwargs["driver"]

    # Handle the new added file
    def on_created(self, event):
        print("New file received - %s." % event.src_path)

        time.sleep(2)

        file_name = str(os.path.basename(event.src_path))
        if file_name.startswith("TWCFIN"):
            self.driver.process_file(event.src_path)

        time.sleep(5)
