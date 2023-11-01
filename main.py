import ctypes
from threading import Thread
from time import sleep
import sys


class IdleSpam:
    def __init__(self):
        options = self.__parse_commandline_args()

        self.interval = float(options.get(
            "i") or options.get("interval") or 30)
        self.key = int(options.get("k") or options.get("key") or "0x14", 16)

        self.__input_thread = None
        self.__process_thread = None

    def __parse_commandline_args(self):
        arguments = sys.argv
        options = {}
        for idx, arg in enumerate(arguments):
            if arg.startswith("--") and arg.find("=") != -1:
                pair = arg.split("=")
                options[pair[0].replace("-", "")] = pair[1]
            elif arg.startswith("-") and not arg.startswith("--") and idx + 1 < len(arguments) and not arguments[idx + 1].startswith("-"):
                options[arg.replace("-", "")] = arguments[idx + 1]
        return options

    def get_input(self):
        try:
            _ = input("Enter any key to stop: ")
            sys.exit(0)
        except Exception:
            return

    def initialize_process(self):
        try:
            self.__input_thread = Thread(target=self.get_input, daemon=True)
            self.__input_thread.start()
            self.__process_thread = Thread(
                target=self.press_key_intermittently, daemon=True)
            self.__process_thread.start()
            self.__input_thread.join()
        except KeyboardInterrupt:
            sys.exit(0)

    def press_key_intermittently(self):
        try:
            while True:
                sleep(self.interval)
                ctypes.windll.user32.keybd_event(self.key, 0, 0, 0)
                ctypes.windll.user32.keybd_event(self.key, 0, 0x0002, 0)
        except Exception as e:
            return


idle_spam_handler = IdleSpam()
idle_spam_handler.initialize_process()
