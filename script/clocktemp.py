#!/usr/bin/python3

"""
# ClockTemp - Copyright (c) 2025 Arthur Dantas
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# See <https://www.gnu.org/licenses/> for details.
"""

from datetime import datetime
from temperature import get_weather
from clock import render_time
import argparse
import curses
import time

def parse_args():
    # Args to command line
    parser = argparse.ArgumentParser(description="ClockTemp is a simple and customizable TUI clock based on tty-clock")
    parser.add_argument("-tf", default="12", help="Time format: 12 (default) for 12-hour clock, 24 for 24-hour clock")
    parser.add_argument("-df", default="mm/dd", help="Date format: dd/mm for day/month/year, mm/dd (default) for month/day/year")
    parser.add_argument("-tu", default="c", help="Temperature unit: c (default) for Celsius, f for Fahrenheit")
    parser.add_argument("-s", default="true", help="Show/Hide seconds (default=True)")
    parser.add_argument("-lat", default="0", help="Latitude of your current location")
    parser.add_argument("-lon", default="0", help="Longitude of your current location")
    parser.add_argument("-c", default="white", help="Clock color scheme: white (default), black, red, yellow, green, cyan, blue, magenta")
    parser.add_argument("-b", default="default", help="Background color scheme: default (terminal default), white, black, red, yellow, green, cyan, blue, magenta")

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

def main(stdscr):
    args = parse_args()   # Capture args from command line

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
        "default": -1, # -1 = terminal default color
        "white": curses.COLOR_WHITE,
        "black": curses.COLOR_BLACK,
        "red": curses.COLOR_RED,
        "yellow": curses.COLOR_YELLOW,
        "green": curses.COLOR_GREEN,
        "cyan": curses.COLOR_CYAN,
        "blue": curses.COLOR_BLUE,
        "magenta": curses.COLOR_MAGENTA
    }

    curses.start_color()
    curses.use_default_colors()

    if curses.has_colors():
        text_color = color_map[args.c]
        backgrond_color = bg_color_map[args.b]
        curses.init_pair(1, text_color, backgrond_color)
        # Apply background color to the entire screen if not default
        if args.b != "default":
            stdscr.bkgd(' ', curses.color_pair(1))

    curses.curs_set(0)    # Remove cursor
    stdscr.timeout(1000)  # 1 second tick

    last_time = ""
    last_temp = ""
    last_temp_update = 0
    current_temp = "N/A"  # If temperature isn't available
    last_height, last_width = stdscr.getmaxyx()

    while True:
        start_time = time.time()

        # Updates temperature every 10 minuts
        if time.time() - last_temp_update >= 600:
            lat = args.lat
            lon = args.lon
            current_temp = get_weather(lat, lon)
            # Convert temperature to fahrenheit or stay in celsius
            if isinstance(current_temp, (int, float)):
                if args.tu == "f":
                    temp_format = (current_temp * 9/5) + 32
                else:
                    temp_format = current_temp
            else:
                temp_format = current_temp
            last_temp_update = time.time()

        # Terminal size
        height, width = stdscr.getmaxyx()

        # Check if the window size has changed
        resized = height != last_height or width != last_width
        if resized:
            stdscr.clear()  # Clear screen to avoid artifacts on resize
            last_height, last_width = height, width

        # Date and Temperature
        date_format = "%m/%d/%Y" if args.df == "mm/dd" else "%d/%m/%Y"
        current_date = datetime.today().strftime(date_format)
        if args.tu == "f" and temp_format != "N/A":
            temp_unit = "ºF"
        elif args.tu == "c" and temp_format != "N/A":
            temp_unit = "ºC"
        else:
            temp_unit = ""
        dateTemp = f"{current_date} | {temp_format:.1f}{temp_unit}" if isinstance(temp_format, (int, float)) else f"{current_date} | {temp_format}{temp_unit}"

        # Hour format based on flag
        if args.tf == "24" and args.s == "true":
            time_format = "%H:%M:%S"
        elif args.tf == "24" and args.s == "false":
            time_format = "%H:%M"
        elif args.tf == "12" and args.s == "true":
            time_format = "%I:%M:%S"
        else:
            time_format = "%I:%M"

        # Centralize clock on terminal
        current_time_lines = render_time(time_format)
        
        clock_height = len(current_time_lines)
        clock_width = len(current_time_lines[0])

        clock_start_y = (height - clock_height) // 2
        clock_start_x = (width - clock_width) // 2

        # Centralize date and temperature on terminal

        dateTemp_width = len(dateTemp)

        dateTemp_start_x = (width - dateTemp_width) // 2

        current_time_str = "\n".join(current_time_lines)
        if current_time_str != last_time or dateTemp != last_temp or resized:
            # Overwrites only the necessary areas with the defined color
            for i, line in enumerate(current_time_lines):
                stdscr.addstr(clock_start_y + i, clock_start_x, " " * clock_width, curses.color_pair(1))
                stdscr.addstr(clock_start_y + i, clock_start_x, line, curses.color_pair(1))
            last_time = current_time_str

            stdscr.addstr(clock_start_y + 6, dateTemp_start_x - 1, " " * dateTemp_width, curses.color_pair(1))
            stdscr.addstr(clock_start_y + 6, dateTemp_start_x - 1, dateTemp, curses.color_pair(1))
            last_temp = dateTemp

        # Refresh terminal
        stdscr.refresh()

        # Close TUI pressing 'q'
        key = stdscr.getch()
        if key == ord('q'):
            break

        # 1 second for each iteration
        elapsed_time = time.time() - start_time
        sleep_time = max(0, 1.0 - elapsed_time)
        time.sleep(sleep_time)

curses.wrapper(main)
