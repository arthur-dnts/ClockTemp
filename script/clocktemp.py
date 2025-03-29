#!/usr/bin/python3
from datetime import datetime
from temperature import get_weather
from clock import render_time
import argparse
import curses
import time

def parse_args():
    parser = argparse.ArgumentParser(description="ClockTemp is a simple and customizable TUI clock based on tty-clock")
    parser.add_argument("-tf", choices=["12", "24"], default="24", help="Time format: 12 for 12-hour clock, 24 for 24-hour clock")
    parser.add_argument("-df", choices=["DD/MM", "MM/DD"], default="MM/DD", help="Date format: DD/MM for day/month/year, MM/DD for month/day/year")
    parser.add_argument("-lat", default="0", help="Latitude of your current location")
    parser.add_argument("-lon", default="0", help="Longitude of your current location")
    parser.add_argument("-color", choices=["white", "red", "yellow", "green", "cyan", "blue", "magenta"], default="white", help="Clock color scheme: white, red, orange, yellow, green, blue or purple")
    return parser.parse_args()

def main(stdscr):
    args = parse_args()   # Capture args from command line

    # Change clock color scheme
    if args.color == "white":
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    elif args.color == "red":
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    elif args.color == "yellow":
        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    elif args.color == "green":
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    elif args.color == "cyan":
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    elif args.color == "blue":
        curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
    else:
        curses.init_pair(1, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    stdscr.attron(curses.color_pair(1))

    curses.curs_set(0)    # Remove cursor
    stdscr.timeout(1000)  # 1 second tick

    last_time = ""
    last_temp_update = 0
    current_temp = "N/A"  # If temperature isn't avaiable

    while True:
        start_time = time.time()

        # Updates temperature every 10 minuts
        if time.time() - last_temp_update >= 600:
            lat = args.lat
            lon = args.lon
            current_temp = get_weather(lat, lon)
            last_temp_update = time.time()

        # Terminal size
        height, width = stdscr.getmaxyx()

        # Date and Temperature
        date_format = "%m/%d/%Y" if args.df == "MM/DD" else "%d/%m/%Y"
        current_date = datetime.today().strftime(date_format)
        dateTemp = f"{current_date} | {current_temp:.1f} ºC" if isinstance(current_temp, (int, float)) else f"{current_date} | {current_temp}"

        # Hour format based on flag
        time_format = "%H:%M:%S" if args.tf == "24" else "%I:%M:%S %p"
        current_time_str = datetime.now().strftime(time_format)

        # Clock
        current_time_lines = render_time()
        
        clock_height = len(current_time_lines)
        clock_width = len(current_time_lines[0])

        clock_start_y = (height - clock_height) // 2
        clock_start_x = (width - clock_width) // 2

        if "\n".join(current_time_lines) != last_time:
            stdscr.clear()
            for i, line in enumerate(current_time_lines):
                stdscr.addstr(clock_start_y + i, clock_start_x, line)
            last_time = "\n".join(current_time_lines)
            stdscr.addstr(clock_start_y + 6, clock_start_x + 18, dateTemp)

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
