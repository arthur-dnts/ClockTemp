#!/usr/bin/python3

"""
# ClockTemp - Copyright (c) 2025 Arthur Dantas
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# See <https://www.gnu.org/licenses/> for details.
"""

from modes import draw_clock, draw_calendar, draw_stopwatch, draw_timer
from datetime import datetime
from tools import Keys
import argparse
import curses
import time
import sys

# Add the path to the clocktemp module
sys.path.append("/usr/local/share/clocktemp")

def parse_args():
    # Args to command line
    parser = argparse.ArgumentParser(description="ClockTemp is a simple and customizable TUI clock based on tty-clock", add_help=False)
    parser.add_argument("-h", "--help", action="store_true", help="Show this help message and exit")
    parser.add_argument("-tf", default="12", help="Time format: 12 (default) for 12-hour clock, 24 for 24-hour clock")
    parser.add_argument("-df", default="mm/dd", help="Date format: dd/mm for day/month/year, mm/dd (default) for month/day/year")
    parser.add_argument("-tu", default="c", help="Temperature unit: c (default) for Celsius, f for Fahrenheit")
    parser.add_argument("-s", default="true", help="Show/Hide seconds (default=True)")
    parser.add_argument("-a", default="true", help="Stop timer/stopwatch after reset (default=True)")
    parser.add_argument("-lat", default="0", help="Latitude of your current location")
    parser.add_argument("-lon", default="0", help="Longitude of your current location")
    parser.add_argument("-c", default="white", help="Text color: white (default), black, red, yellow, green, cyan, blue, magenta")
    parser.add_argument("-b", default="default", help="Background color: default (terminal default), white, black, red, yellow, green, cyan, blue, magenta")

    args = parser.parse_args()
    return validate_args(args, parser)

def validate_args(args, parser):
    # Valid arguments
    valid_options = {
        "tf": {"12", "24"},
        "df": {"dd/mm", "mm/dd"},
        "tu": {"c", "f"},
        "s": {"true", "false"},
        "a": {"true", "false"},
        "c": {"white", "black", "red", "yellow", "green", "cyan", "blue", "magenta"},
        "b": {"default", "white", "black", "red", "yellow", "green", "cyan", "blue", "magenta"}
    }

    # Convert arguments to lowercase to ensure case-insensitivity
    for key in valid_options:
        setattr(args, key, getattr(args, key).lower())

    for key, valid_values in valid_options.items():
        value = getattr(args, key)
        if value not in valid_values:
            parser.error(f"Invalid {key} option: {value}. Choose from {list(valid_values)}")

    return args

def print_help():
    help_text = """
        ClockTemp - A simple and customizable TUI clock based on tty-clock
        Version: 1.1.3

        Usage: clocktemp [OPTIONS]

        Options:
        -h, --help           Show this help message and exit
        -tf [12, 24]         Time format: 12 (default) for 12-hour clock, 24 for 24-hour clock
        -df [mm/dd, dd/mm]   Date format: mm/dd (default) for month/day/year, dd/mm for day/month/year
        -tu [c,f]            Temperature unit: c (default) for Celsius, f for Fahrenheit
        -s [true, false]     Show/Hide seconds: true (default) to show, false to hide
        -a [true, false]     Stop timer/stopwatch after reset (default: true)
        -lat LATITUDE        Latitude of your current location (default: 0)
        -lon LONGITUDE       Longitude of your current location (default: 0)
        -c COLOR             Text color: white (default), black, red, yellow, green, cyan, blue, magenta
        -b COLOR             Background color: default (terminal default), white, black, red, yellow, green, cyan, blue, magenta

        keys:
        w                    Switch to clock mode
        c                    Switch to calendar mode
        s                    Switch to stopwatch mode
        t                    Switch to timer mode
        r                    Reset (in stopwatch or timer mode)
        SPACEBAR             Pause/Resume (in stopwatch or timer mode)
        < or ,               Show previous month (calendar mode only)
        > or .               Show next month (calendar mode only)
        q or ESC             Quit the program

        Note:
        - Options are case-insensitive (e.g., -c RED or -c red both work).
        - In calendar mode, the current day is highlighted with inverted colors (background from -c, text from -b).

        Command example:
        clocktemp -tf 24 -df dd/mm -tu c -s true -lat 12.345 -lon -67.891 -c black -b white
    """
    
    print(help_text)
    sys.exit(0)

class initial_state:
    def __init__(self, stdscr):
        # Initialize variables for clock
        self.last_temp = ""                               # Stores the last temperature
        self.last_temp_update = 0                         # Temperature update time
        self.last_height, self.last_width = stdscr.getmaxyx()  # Terminal size
        self.mode = "clock"                               # Default mode

        # Initialize variables for calendar
        self.calendar_year = datetime.now().year          # Calendar current year
        self.calendar_month = datetime.now().month        # Calendar current month

        # Initialize variables for stopwatch
        self.stopwatch_start = time.time()
        self.stopwatch_accumulated = 0
        self.stopwatch_running = False

        # Initialize variables for timer
        self.timer_running = False
        self.total_time = 0
        self.initial_time = 0
        self.timer_input_mode = False  # Flag to control timer input screen

def main(stdscr, args):

    state = initial_state(stdscr)

    # Map text color
    color_map = {
        "white": curses.COLOR_WHITE,
        "black": curses.COLOR_BLACK,
        "red": curses.COLOR_RED,
        "yellow": curses.COLOR_YELLOW,
        "green": curses.COLOR_GREEN,
        "cyan": curses.COLOR_CYAN,
        "blue": curses.COLOR_BLUE,
        "magenta": curses.COLOR_MAGENTA
    }

    # Map background color
    bg_color_map = {
        "default": -1, # terminal default color (transparent)
        "white": curses.COLOR_WHITE,
        "black": curses.COLOR_BLACK,
        "red": curses.COLOR_RED,
        "yellow": curses.COLOR_YELLOW,
        "green": curses.COLOR_GREEN,
        "cyan": curses.COLOR_CYAN,
        "blue": curses.COLOR_BLUE,
        "magenta": curses.COLOR_MAGENTA
    }

    # Initialize colors
    curses.start_color()
    curses.use_default_colors()
    text_color = color_map[args.c]
    background_color = bg_color_map[args.b]
    curses.init_pair(1, text_color, background_color)
    inverted_text_color = background_color if background_color != -1 else curses.COLOR_BLACK
    inverted_background_color = text_color
    curses.init_pair(2, inverted_text_color, inverted_background_color)

    if args.b != "default":
        stdscr.bkgd(" ", curses.color_pair(1))

    curses.curs_set(0) # Hide cursor
    stdscr.timeout(100) # 1 second ticker

    while True:
        start_time = time.time()

        key = stdscr.getch()

        # Handle key events
        if key in (Keys.q, Keys.Q, Keys.ESC):    # Quit the program
            break
        elif key in (Keys.w, Keys.W):  # Change mode to clock mode
            state.mode = "clock"
            state.timer_input_mode = False
            curses.curs_set(0)
        elif key in (Keys.c, Keys.C):  # Change mode to calendar
            state.mode = "calendar"
            state.timer_input_mode = False
            curses.curs_set(0)
        elif key in (Keys.s, Keys.S):  # Change mode to stopwatch
            state.mode = "stopwatch"
            state.timer_input_mode = False
            curses.curs_set(0)
        elif key in (Keys.t, Keys.T):  # Change mode to timer
            state.mode = "timer"
            state.timer_input_mode = True

        # Modes functions
        elif key in (Keys.r, Keys.R):
            if state.mode == "stopwatch": # Reset stopwatch
                state.stopwatch_start = time.time()
                state.stopwatch_accumulated = 0
                state.stopwatch_running = args.a == "false"
            elif state.mode == "timer" and not state.timer_input_mode: # Reset timer
                state.total_time = state.initial_time
                state.timer_running = args.a == "false"

        elif key == Keys.SPACE: # Pause/Resume stopwatch or timer
            if state.mode == "stopwatch":
                if state.stopwatch_running:
                    state.stopwatch_accumulated += time.time() - state.stopwatch_start
                    state.stopwatch_running = False
                else:
                    state.stopwatch_start = time.time()
                    state.stopwatch_running = True
            elif state.mode == "timer" and not state.timer_input_mode:
                state.timer_running = not state.timer_running

        elif state.mode == "calendar" and key in (Keys.LESS, Keys.COMMA): # Previous month
            state.calendar_month -= 1
            if state.calendar_month < 1:
                state.calendar_month = 12
                state.calendar_year -= 1

        elif state.mode == "calendar" and key in (Keys.GREATER, Keys.DOT): # Next month
            state.calendar_month += 1
            if state.calendar_month > 12:
                state.calendar_month = 1
                state.calendar_year += 1

        stdscr.erase()

        height, width = stdscr.getmaxyx() # Get terminal size
        resized = height != state.last_height or width != state.last_width # Check if terminal size has changed
        if resized: # If resized clear terminal to avoid artifacts
            stdscr.clear()
            state.last_height, state.last_width = height, width

        if state.mode == "clock":
            state.last_temp, state.last_temp_update = draw_clock(stdscr, args, height, width, state)
        
        elif state.mode == "calendar":
            draw_calendar(stdscr, height, width, state)
        
        elif state.mode == "stopwatch":
            state.stopwatch_accumulated, state.stopwatch_running = draw_stopwatch(stdscr, height, width, state)

        elif state.mode == "timer":
            state.total_time, state.initial_time, state.timer_running, state.timer_input_mode = draw_timer(stdscr, height, width, state)
            # if timer is over return to clock mode
            if not state.timer_running and state.total_time == 0 and not state.timer_input_mode:
                state.mode = "clock"
    
        stdscr.refresh()

        elapsed_time = time.time() - start_time
        sleep_time = max(0, 1.0 - elapsed_time)
        time.sleep(sleep_time)

if __name__ == "__main__":
    args = parse_args()
    if args.help:
        print_help()
    else:
        curses.wrapper(main, args)
