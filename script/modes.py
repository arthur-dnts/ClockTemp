"""
# modes.py - Copyright (c) 2025 Arthur Dantas
# This file is part of ClockTemp, licensed under the GNU General Public License v3.
# See <https://www.gnu.org/licenses/> for details.
"""

from clock import render_digits, format_clock, format_time
from temperature import get_weather
from cal import render_calendar
from datetime import datetime
from curses.textpad import Textbox, rectangle
from math import ceil
from tools import Keys
import curses
import time

# Function to center and highlight text
def center_highlighted_text(stdscr, height, width, text, description, start_y_offset, args):
    # Ensure text is a list to handle multiple lines
    if isinstance(text, str):
        text = [text]

    for i, line in enumerate(text):
        full_line = line + description
        line_width = len(full_line)
        start_x = (width - line_width) // 2

        if start_y_offset + i < height and start_x + line_width <= width:
            stdscr.addstr(start_y_offset + i, start_x, line, curses.color_pair(1) | curses.A_BOLD)
            stdscr.addstr(start_y_offset + i, start_x + len(line), description, curses.color_pair(1) | (curses.A_DIM if args.bd == "false" else curses.A_BOLD))

def help_menu(stdscr, height, width, args):
    # Centralize help menu on terminal
    logo = """
    ▟███ ██    ▟███▙ ▟███ ██ ▟█ ██████ ▟███▙ █▙   ▟█ ▟███▙ 
    ██   ██    ██ ██ ██   ███▛    ██   ██ ██ ███ ███ ██ ██ 
    ██   ██    ██ ██ ██   ██ █▙   ██   ██▛▘  ██ █ ██ ████▛ 
    ▜███ ▜████ ▜███▛ ▜███ ██ ██   ██   ▜████ ██   ██ ██    
                                             Version 1.1.4 
    """

    logo_start_x = width - 2
    logo_start_y = (height -12) // 2

    center_highlighted_text(stdscr, height, logo_start_x, logo.splitlines(), "", logo_start_y, args)
    center_highlighted_text(stdscr, height, width - 29, "W : ", "Clock Mode", logo_start_y + 7, args)
    center_highlighted_text(stdscr, height, width + 25, "C : ", "Calendar Mode", logo_start_y + 7, args)
    center_highlighted_text(stdscr, height, width - 25, "S : ", "Stopwatch Mode", logo_start_y + 9, args)
    center_highlighted_text(stdscr, height, width + 21, "T : ", "Timer Mode", logo_start_y + 9, args)
    center_highlighted_text(stdscr, height, width - 2, "Q / ESC : ", "Close program", logo_start_y + 11, args)

def draw_clock(stdscr, height, width, state, args):

    temp_format = state.last_temp

    # Update temperature every 10 minutes
    if time.time() - state.last_temp_update >= 600:
        try:
            current_temp = get_weather(args.lat, args.lon)
            if isinstance(current_temp, (int, float)):
                if args.tu == "f":
                    temp_format = f"{float((current_temp * 9/5) + 32):.1f}"
                else:
                    temp_format = f"{float(current_temp):.1f}"
            else:
                temp_format = "N/A"
            state.last_temp_update = time.time()
        except:
            temp_format = "N/A"

    # Change temperature format based on args.tu
    temp_unit = "ºF" if args.tu == "f" and temp_format != "N/A" else "ºC" if args.tu == "c" and temp_format != "N/A" else ""

    # Change date format based on args.df
    date_format = "%m/%d/%Y" if args.df == "mm/dd" else "%d/%m/%Y"
    current_date = datetime.today().strftime(date_format)

    date_temp = f"{current_date} · {temp_format}{temp_unit}" if isinstance(temp_format, (int, float)) else f"{current_date} · {temp_format}{temp_unit}"

    # Change time format based on args.tf and args.s
    time_format = "%H:%M:%S" if args.tf == "24" and args.s == "true" else "%H:%M" if args.tf == "24" else "%I:%M:%S" if args.s == "true" else "%I:%M"

    # Add meridiem indicator for 12-hour format
    if args.tf == "12":
        meridian = datetime.now().strftime("%p")
        if meridian == "AM":
            meridian_indicator = "[AM]"
        else:
            meridian_indicator = "[PM]"
        date_temp += f" · {meridian_indicator}"

    time_format = format_clock(datetime.now(), time_format)
    current_time_lines = render_digits(time_format)

    # Centralize clock, date and temperature on terminal
    clock_start_y = (height - len(current_time_lines)) // 2

    center_highlighted_text(stdscr, height, width, current_time_lines, "", clock_start_y, args)
    center_highlighted_text(stdscr, height, width, "", date_temp, clock_start_y + 6, args)

    return temp_format, state.last_temp_update

def draw_calendar(stdscr, height, width, state, args):

    # Centralize calendar on terminal
    calendar_lines, calendar_attrs = render_calendar(state.calendar_year, state.calendar_month)
    calendar_height = len(calendar_lines)
    calendar_width = max(len(line) for line in calendar_lines)
    calendar_start_y = (height - calendar_height) // 2 - 1
    calendar_start_x = (width - calendar_width) // 2

    # Centralize hint on terminal
    calendar_hint_start_y = calendar_start_y + calendar_height + 1

    center_highlighted_text(stdscr, height, width + 1, "<             >", "", calendar_hint_start_y, args)
    center_highlighted_text(stdscr, height, width + 1, "", "Prev | Next", calendar_hint_start_y, args)

    for i, line in enumerate(calendar_lines):
        if i < 2:
            # Header
            if calendar_start_y + i < height and calendar_start_x + len(line) <= width:
                center_highlighted_text(stdscr, height, width, "", line, calendar_start_y + i, args)
        else:
            # Current day highlighted
            if calendar_start_y + i < height and calendar_start_x + len(line) <= width:
                x = calendar_start_x
                for j, char in enumerate(line):
                    attr = curses.color_pair(calendar_attrs[i-2][j]) if (i-2) < len(calendar_attrs) and j < len(calendar_attrs[i-2]) else curses.color_pair(1)
                    if x < width:
                        stdscr.addch(calendar_start_y + i, x, char, attr)
                    x += 1

def draw_stopwatch(stdscr, height, width, state, args):

    if state.stopwatch_running:
        state.stopwatch_total_time = int(time.time() - state.stopwatch_start + state.stopwatch_accumulated)
    else:
        state.stopwatch_total_time = int(state.stopwatch_accumulated)

    # Centralize stopwatch message on terminal
    stopwatch_total_time = state.stopwatch_total_time
    time_str = format_time(stopwatch_total_time)
    current_stop_lines = render_digits(time_str)

    # Centralize clock and hints on terminal
    stopwatch_start_y = (height - len(current_stop_lines)) // 2

    center_highlighted_text(stdscr, height, width, current_stop_lines, "", stopwatch_start_y, args)
    center_highlighted_text(stdscr, height, width, "", "Mode : Stopwatch", stopwatch_start_y - 2, args)
    center_highlighted_text(stdscr, height, width, "SPACEBAR : ", "Pause/Resume", stopwatch_start_y + 6, args)
    center_highlighted_text(stdscr, height, width, "R : ", "Reset", stopwatch_start_y + 7, args)

    return state.stopwatch_accumulated, state.stopwatch_running

def draw_timer(stdscr, height, width, state, args):
    try:
        # Screen for inputting timer time
        if state.timer_input_mode and not state.timer_running:

            # Exit from text input screen
            def exit_input(ch):
                if ch == Keys.ESC:
                    raise KeyboardInterrupt
                return ch

            # Create a textbox for timer input
            rect_height = 1
            rect_width = 4
            rect_start_y = (height - rect_height) // 2
            rect_start_x = (width - rect_width - 2) // 2
            rect_end_y = rect_start_y + rect_height + 1
            rect_end_x = rect_start_x + rect_width + 1

            rectangle(stdscr, rect_start_y, rect_start_x, rect_end_y, rect_end_x)

            # Centralize hints on terminal
            center_highlighted_text(stdscr, height, width, "Enter time in minutes", "", rect_start_y - 2, args)
            center_highlighted_text(stdscr, height, width, "ESC : ", "Exit", rect_start_y + 4, args)

            # Create and process text field
            win = curses.newwin(rect_height, rect_width, rect_start_y + 1, rect_start_x + 1)
            box = Textbox(win)
            curses.curs_set(1) # Display cursor
            stdscr.refresh()
            win.refresh()
            box.edit(exit_input)

            # Convert input from minutes to seconds
            try:
                minutes = float(box.gather().strip())
                if minutes <= 0:
                    state.timer_input_mode = True
                    curses.curs_set(0)
                    return state.timer_total_time, state.initial_time, state.timer_running, state.timer_input_mode
                state.timer_total_time = int(minutes * 60)
                state.initial_time = state.timer_total_time
                state.timer_running = True
                state.timer_input_mode = False
                curses.curs_set(0)
            except ValueError:
                state.timer_input_mode = False
                curses.curs_set(0)
                return state.timer_total_time, state.initial_time, state.timer_running, state.timer_input_mode

        else:
            # Render timer
            if state.timer_running and state.timer_total_time > 0:
                state.timer_total_time -= 1

            # Timer finished message
            elif state.timer_total_time <= 0 and state.timer_running:
                state.timer_running = False
                state.timer_input_mode = True
                stdscr.clear()

                # Centralize end message on terminal
                end_start_y = (height) // 2
                wait_msg = "Returning to clock mode in {} seconds..."

                center_highlighted_text(stdscr, height, width, "Timer finished.", "", end_start_y, args)
                for i in range(50):
                    if stdscr.getch() != -1:
                        break
                    center_highlighted_text(stdscr, height, width, "", wait_msg.format(ceil((50-i)/10)), end_start_y + 1, args)
                    stdscr.refresh()
                    curses.beep()

            timer_total_time = state.timer_total_time
            time_str = format_time(timer_total_time)
            current_timer_lines = render_digits(time_str)

            # Centralize timer and hints on terminal
            timer_start_y = (height - len(current_timer_lines)) // 2

            center_highlighted_text(stdscr, height, width, current_timer_lines, "", timer_start_y, args)
            center_highlighted_text(stdscr, height, width, "", "Mode : Timer", timer_start_y - 2, args)
            center_highlighted_text(stdscr, height, width, "SPACEBAR : ", "Pause/Resume", timer_start_y + 6, args)
            center_highlighted_text(stdscr, height, width, "R : ", "Reset", timer_start_y + 7, args)

        return state.timer_total_time, state.initial_time, state.timer_running, state.timer_input_mode

    except (KeyboardInterrupt, curses.error):
        curses.curs_set(0)
        return state.timer_total_time, state.initial_time, state.timer_running, False
