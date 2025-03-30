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
    parser.add_argument("-tf", choices=["12", "24"], default="12", help="Time format: 12 (default) for 12-hour clock, 24 for 24-hour clock")
    parser.add_argument("-df", choices=["dd/mm", "mm/dd"], default="mm/dd", help="Date format: dd/mm for day/month/year, mm/dd (default) for month/day/year")
    parser.add_argument("-tu", choices=["c", "f"], default="c", help="Temperature unity: c (default) for Celsius, f for fahrenheit")
    parser.add_argument("-s", choices=["true", "false"], default="true", help="Show/Hide seconds (default=True)")
    parser.add_argument("-lat", default="0", help="Latitude of your current location")
    parser.add_argument("-lon", default="0", help="Longitude of your current location")
    parser.add_argument("-c", choices=["white", "red", "yellow", "green", "cyan", "blue", "magenta"], default="white", help="Clock color scheme: white (default), red, yellow, green, cyan, blue and magenta")
    return parser.parse_args()

def main(stdscr):
    args = parse_args()   # Capture args from command line

    # Change clock color scheme
    if args.c == "white":
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    elif args.c == "red":
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    elif args.c == "yellow":
        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    elif args.c == "green":
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    elif args.c == "cyan":
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    elif args.c == "blue":
        curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
    else:
        curses.init_pair(1, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    stdscr.attron(curses.color_pair(1))

    curses.curs_set(0)    # Remove cursor
    stdscr.timeout(1000)  # 1 second tick

    last_time = ""
    last_temp_update = 0
    current_temp = "N/A"  # If temperature isn't available

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

        # Date and Temperature
        date_format = "%m/%d/%Y" if args.df == "mm/dd" else "%d/%m/%Y"
        current_date = datetime.today().strftime(date_format)
        if args.tu == "f" and temp_format != "N/A":
            temp_unity = "ºF"
        elif args.tu == "c" and temp_format != "N/A":
            temp_unity = "ºC"
        else:
            temp_unity = ""
        dateTemp = f"{current_date} | {temp_format:.1f}{temp_unity}" if isinstance(temp_format, (int, float)) else f"{current_date} | {temp_format}{temp_unity}"

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

        if "\n".join(current_time_lines) != last_time:
            stdscr.clear()
            for i, line in enumerate(current_time_lines):
                stdscr.addstr(clock_start_y + i, clock_start_x, line)
            last_time = "\n".join(current_time_lines)
            stdscr.addstr(clock_start_y + 6, dateTemp_start_x - 1, dateTemp)

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
