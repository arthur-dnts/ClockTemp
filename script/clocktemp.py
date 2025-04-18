#!/usr/bin/python3

"""
# ClockTemp - Copyright (c) 2025 Arthur Dantas
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# See <https://www.gnu.org/licenses/> for details.
"""

from temperature import get_weather
from cal import render_calendar
from clock import render_time
from datetime import datetime
import argparse
import curses
import time
import sys

# Add the path to the clocktemp module
sys.path.append('/usr/local/share/clocktemp')

def parse_args():
    # Args to command line
    parser = argparse.ArgumentParser(description="ClockTemp is a simple and customizable TUI clock based on tty-clock", add_help=False)
    parser.add_argument("-h", "--help", action="store_true", help="Show this help message and exit")
    parser.add_argument("-tf", default="12", help="Time format: 12 (default) for 12-hour clock, 24 for 24-hour clock")
    parser.add_argument("-df", default="mm/dd", help="Date format: dd/mm for day/month/year, mm/dd (default) for month/day/year")
    parser.add_argument("-tu", default="c", help="Temperature unit: c (default) for Celsius, f for Fahrenheit")
    parser.add_argument("-s", default="true", help="Show/Hide seconds (default=True)")
    parser.add_argument("-lat", default="0", help="Latitude of your current location")
    parser.add_argument("-lon", default="0", help="Longitude of your current location")
    parser.add_argument("-c", default="white", help="Text color: white (default), black, red, yellow, green, cyan, blue, magenta")
    parser.add_argument("-b", default="default", help="Background color: default (terminal default), white, black, red, yellow, green, cyan, blue, magenta")

    args = parser.parse_args()

    # Convert to lowercase and validate
    valid_tf = {"12", "24"}
    valid_df = {"dd/mm", "mm/dd"}
    valid_tu = {"c", "f"}
    valid_s = {"true", "false"}
    valid_colors = {"white", "black", "red", "yellow", "green", "cyan", "blue", "magenta"}
    valid_bg_colors = {"default", "white", "black", "red", "yellow", "green", "cyan", "blue", "magenta"}

    args.tf = args.tf.lower()
    if args.tf not in valid_tf:
        parser.error(f"Invalid time format: {args.tf}. Choose from {list(valid_tf)}")

    args.df = args.df.lower()
    if args.df not in valid_df:
        parser.error(f"Invalid date format: {args.df}. Choose from {list(valid_df)}")

    args.tu = args.tu.lower()
    if args.tu not in valid_tu:
        parser.error(f"Invalid temperature unit: {args.tu}. Choose from {list(valid_tu)}")

    args.s = args.s.lower()
    if args.s not in valid_s:
        parser.error(f"Invalid seconds option: {args.s}. Choose from {list(valid_s)}")

    args.c = args.c.lower()
    if args.c not in valid_colors:
        parser.error(f"Invalid color: {args.c}. Choose from {list(valid_colors)}")

    args.b = args.b.lower()
    if args.b not in valid_bg_colors:
        parser.error(f"Invalid color: {args.b}. Choose from {list(valid_bg_colors)}")

    return args

def print_help():
    help_text = """
        ClockTemp - A simple and customizable TUI clock based on tty-clock

        Usage: clocktemp [OPTIONS]

        Options:
        -h, --help          Show this help message and exit
        -tf {12,24}         Time format: 12 (default) for 12-hour clock, 24 for 24-hour clock
        -df {mm/dd,dd/mm}   Date format: mm/dd (default) for month/day/year, dd/mm for day/month/year
        -tu {c,f}           Temperature unit: c (default) for Celsius, f for Fahrenheit
        -s {true,false}     Show/Hide seconds: true (default) to show, false to hide
        -lat LATITUDE       Latitude of your current location (default: 0)
        -lon LONGITUDE      Longitude of your current location (default: 0)
        -c COLOR            Text color: white (default), black, red, yellow, green, cyan, blue, magenta
        -b COLOR            Background color: default (terminal default), white, black, red, yellow, green, cyan, blue, magenta

        Interactive keys:
        m                   Toggle between clock and calendar modes
        < or ,              Show previous month (calendar mode only)
        > or .              Show next month (calendar mode only)
        q                   Quit the program

        Note:
        - Options are case-insensitive (e.g., -c RED or -c red both work).
        - In calendar mode, the current day is highlighted with inverted colors (background from -c, text from -b).

        Examples:
        clocktemp -tf 24 -df dd/mm -tu c -s true -lat 12.345 -lon -67.891 -c black -b white
        clocktemp -h
    """

    print(help_text)
    sys.exit(0)

def main(stdscr, args):

    # Initialize variables
    last_time = ""
    last_temp = ""
    last_temp_update = 0
    current_temp = "N/A"
    last_height, last_width = stdscr.getmaxyx()
    mode = "clock"
    calendar_year = datetime.now().year
    calendar_month = datetime.now().month

    # Map clock and background colors
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

    bg_color_map = {
        "default": -1,
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
        stdscr.bkgd(' ', curses.color_pair(1))

    curses.curs_set(0)
    stdscr.timeout(1000)

    while True:
        start_time = time.time()
        stdscr.clear()

        height, width = stdscr.getmaxyx()
        resized = height != last_height or width != last_width
        if resized:
            stdscr.clear()
            last_height, last_width = height, width

        if mode == "clock":
            if time.time() - last_temp_update >= 600:
                lat = args.lat
                lon = args.lon
                try:
                    current_temp = get_weather(lat, lon)
                    if isinstance(current_temp, (int, float)):
                        if args.tu == "f":
                            temp_format = (current_temp * 9/5) + 32
                        else:
                            temp_format = current_temp
                    else:
                        temp_format = current_temp
                    last_temp_update = time.time()
                except:
                    current_temp = "N/A"

            # Change date format based on args.df
            date_format = "%m/%d/%Y" if args.df == "mm/dd" else "%d/%m/%Y"
            current_date = datetime.today().strftime(date_format)

            # Change temperature format based on args.tu
            if args.tu == "f" and temp_format != "N/A":
                temp_unit = "ºF"
            elif args.tu == "c" and temp_format != "N/A":
                temp_unit = "ºC"
            else:
                temp_unit = ""
            dateTemp = f"{current_date} | {temp_format:.1f}{temp_unit}" if isinstance(temp_format, (int, float)) else f"{current_date} | {temp_format}{temp_unit}"

            # Change time format based on args.tf and args.s
            if args.tf == "24" and args.s == "true":
                time_format = "%H:%M:%S"
            elif args.tf == "24" and args.s == "false":
                time_format = "%H:%M"
            elif args.tf == "12" and args.s == "true":
                time_format = "%I:%M:%S"
            else:
                time_format = "%I:%M"

            try:
                # Centralize clock, date and temperature on terminal
                current_time_lines = render_time(time_format)
                clock_height = len(current_time_lines)
                clock_width = len(current_time_lines[0]) if current_time_lines else 0
                clock_start_y = (height - clock_height) // 2
                clock_start_x = (width - clock_width) // 2

                dateTemp_width = len(dateTemp)
                dateTemp_start_x = (width - dateTemp_width) // 2

                current_time_str = "\n".join(current_time_lines)
                # Sempre renderizar o relógio para evitar que ele desapareça
                if clock_start_y >= 0 and clock_start_x >= 0:
                    for i, line in enumerate(current_time_lines):
                        if clock_start_y + i < height and clock_start_x + clock_width <= width:
                            stdscr.addstr(clock_start_y + i, clock_start_x, " " * clock_width, curses.color_pair(1))
                            stdscr.addstr(clock_start_y + i, clock_start_x, line, curses.color_pair(1))
                    if clock_start_y + 6 < height and dateTemp_start_x - 1 + dateTemp_width <= width:
                        stdscr.addstr(clock_start_y + 6, dateTemp_start_x - 1, " " * dateTemp_width, curses.color_pair(1))
                        stdscr.addstr(clock_start_y + 6, dateTemp_start_x - 1, dateTemp, curses.color_pair(1))
                last_time = current_time_str
                last_temp = dateTemp
            except (curses.error, ValueError, IndexError):
                pass

        elif mode == "calendar":
            try:
                # Centralize calendar on terminal
                calendar_lines, calendar_attrs = render_calendar(calendar_year, calendar_month)
                calendar_height = len(calendar_lines)
                calendar_width = max(len(line) for line in calendar_lines)
                calendar_start_y = (height - calendar_height) // 2
                calendar_start_x = (width - calendar_width) // 2

                calendar_msg = "< Prev | Next >"
                calendar_msg_start_x = (width - len(calendar_msg)) // 2
                calendar_msg_start_y = calendar_start_y + calendar_height + 1

                for i, line in enumerate(calendar_lines):
                    if i < 2:
                        if calendar_start_y + i < height and calendar_start_x + len(line) <= width:
                            stdscr.addstr(calendar_start_y + i, calendar_start_x, line, curses.color_pair(1))
                    else:
                        if calendar_start_y + i < height and calendar_start_x + len(line) <= width:
                            x = calendar_start_x
                            for j, char in enumerate(line):
                                attr = curses.color_pair(calendar_attrs[i-2][j]) if j < len(calendar_attrs[i-2]) else curses.color_pair(1)
                                if x < width:
                                    stdscr.addch(calendar_start_y + i, x, char, attr)
                                x += 1
                if calendar_msg_start_y < height and calendar_msg_start_x + len(calendar_msg) <= width:
                    stdscr.addstr(calendar_msg_start_y, calendar_msg_start_x, calendar_msg, curses.color_pair(1))
            except curses.error:
                pass

        stdscr.refresh()

        key = stdscr.getch()
        # Handle key events
        if key == ord("q"):
            break
        elif key == ord("m"):
            mode = "calendar" if mode == "clock" else "clock"
        elif mode == "calendar" and key in (ord("<"), ord(",")):
            calendar_month -= 1
            if calendar_month < 1:
                calendar_month = 12
                calendar_year -= 1
        elif mode == "calendar" and key in (ord(">"), ord(".")):
            calendar_month += 1
            if calendar_month > 12:
                calendar_month = 1
                calendar_year += 1

        elapsed_time = time.time() - start_time
        sleep_time = max(0, 1.0 - elapsed_time)
        time.sleep(sleep_time)

if __name__ == "__main__":
    args = parse_args()
    if args.help:
        print_help()
    else:
        curses.wrapper(main, args)