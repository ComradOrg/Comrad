import time,os,subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

p = None

def run_command():
    global p

    if p!=None: p.terminate()
    
    cmd = 'python3 main.py'
    p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)

class Watcher:
    DIRECTORY_TO_WATCH = "/home/ryan/github/Gyre/client"

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Error")

        self.observer.join()


class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        if event.src_path.endswith('gyre.json'): return None
        if event.src_path.endswith('log.txt'): return None

        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            print("Received created event - %s." % event.src_path)

        elif event.event_type == 'modified':
            # Taken any action here when a file is modified.
            print("   \n\n\n\n\nReceived modified event - %s." % event.src_path)
            run_command()
#


if __name__ == '__main__':
    run_command()
    w = Watcher()
    w.run()

    
