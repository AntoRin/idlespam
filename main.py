import ctypes
from threading import Thread
from time import sleep
import random
import sys
import pyautogui


class PreventIdle:
    def __init__(self):
        options = self.__parse_commandline_args()

        self.interval = float(options.get("i") or options.get("interval") or 30)
        self.key = int(options.get("k") or options.get("key") or "0x14", 16)
        self.no_check_movement = options.get("nocheckmovement")

        self.random_interval = (
            list(map(lambda x: int(x), options.get("random").split(",")))
            if options.get("random") and len(options.get("random").split(",")) == 2
            else None
        )

        self.log = options.get("log")

        if self.log:
            print(
                {
                    "interval": self.interval,
                    "key": hex(self.key),
                    "no_check_movement": self.no_check_movement,
                    "random_interval": self.random_interval,
                    "log": self.log,
                }
            )

        self.__input_thread = None
        self.__process_thread = None
        self.__saved_cursor_pos = None

    def __parse_commandline_args(self):
        arguments = sys.argv
        options = {}
        for idx, arg in enumerate(arguments):
            if arg.startswith("--"):
                if arg.find("=") != -1:
                    pair = arg.split("=")
                    options[pair[0].replace("-", "")] = pair[1]
                else:
                    if idx + 1 < len(arguments) and not arguments[idx + 1].startswith(
                        "-"
                    ):
                        options[arg.replace("-", "")] = arguments[idx + 1]
                    if idx + 1 >= len(arguments) or arguments[idx + 1].startswith("-"):
                        options[arg.replace("-", "")] = True

            elif (
                arg.startswith("-")
                and not arg.startswith("--")
                and idx + 1 < len(arguments)
                and not arguments[idx + 1].startswith("-")
            ):
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
                target=self.press_key_intermittently, daemon=True
            )
            self.__process_thread.start()
            self.__input_thread.join()
        except KeyboardInterrupt:
            sys.exit(0)

    def press_key_intermittently(self):
        try:
            while True:
                sleep(
                    random.randint(self.random_interval[0], self.random_interval[1])
                    if self.random_interval
                    else self.interval
                )

                if self.no_check_movement:
                    self.__perform_key_press(self.key)
                    continue

                curr_cursor_pos = pyautogui.position()

                if (
                    not self.__saved_cursor_pos
                    or curr_cursor_pos == self.__saved_cursor_pos
                ):
                    self.__perform_key_press(self.key)

                self.__saved_cursor_pos = curr_cursor_pos

        except Exception as e:
            return

    def __perform_key_press(self, key):
        ctypes.windll.user32.keybd_event(key, 0, 0, 0)
        ctypes.windll.user32.keybd_event(key, 0, 0x0002, 0)


prevent_idle_handler = PreventIdle()
prevent_idle_handler.initialize_process()
