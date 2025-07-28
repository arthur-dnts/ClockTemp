"""
# modes.py - Copyright (c) 2025 Arthur Dantas
# This file is part of ClockTemp, licensed under the GNU General Public License v3.
# See <https://www.gnu.org/licenses/> for details.
"""

from clock import render_clock, render_stop_timer
from temperature import get_weather
from cal import render_calendar
from datetime import datetime
from curses.textpad import Textbox, rectangle
import curses
import time

def center_text(stdscr, text_lines, height, width, color_pair, start_y_offset):
    for i, line in enumerate(text_lines):
        line_width = len(line)
        start_x = (width - line_width) // 2
        if start_y_offset + i < height and start_x + line_width <= width:
            stdscr.addstr(start_y_offset + i, start_x, " " * line_width, color_pair)
            stdscr.addstr(start_y_offset + i, start_x, line, color_pair)

def draw_clock(stdscr, args, height, width, state):

    temp_format = state.last_temp

    # Update temperature every 10 minutes
    if time.time() - state.last_temp_update >= 600:
        try:
            current_temp = get_weather(args.lat, args.lon)
            if isinstance(current_temp, (int, float)):
                if args.tu == "f":
                    temp_format = "{:04.1f}".format(temp_format, (current_temp * 9/5) + 32)
                else:
                    temp_format = "{:04.1f}".format(float(current_temp))
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

    date_temp = f"{current_date} | {temp_format}{temp_unit}" if isinstance(temp_format, (int, float)) else f"{current_date} | {temp_format}{temp_unit}"

    # Change time format based on args.tf and args.s
    time_format = "%H:%M:%S" if args.tf == "24" and args.s == "true" else "%H:%M" if args.tf == "24" else "%I:%M:%S" if args.s == "true" else "%I:%M"

    current_time_lines = render_clock(time_format)

    # Centralize clock, date and temperature on terminal
    center_text(stdscr, current_time_lines, height, width, curses.color_pair(1), (height - len(current_time_lines)) // 2)
    center_text(stdscr, [date_temp], height, width, curses.color_pair(1), (height - len(current_time_lines)) // 2 + 6)

    return temp_format, state.last_temp_update

def draw_calendar(stdscr, height, width, state):

    # Centralize calendar on terminal
    calendar_lines, calendar_attrs = render_calendar(state.calendar_year, state.calendar_month)
    calendar_height = len(calendar_lines)
    calendar_width = max(len(line) for line in calendar_lines)
    calendar_start_y = (height - calendar_height) // 2 - 1
    calendar_start_x = (width - calendar_width) // 2

    # Centralize hint on terminal
    calendar_hint = "< Prev | Next >"
    calendar_hint_start_x = (width - len(calendar_hint)) // 2
    calendar_hint_start_y = calendar_start_y + calendar_height + 1

    for i, line in enumerate(calendar_lines):
        if i < 2:
            # Header
            if calendar_start_y + i < height and calendar_start_x + len(line) <= width:
                stdscr.addstr(calendar_start_y + i, calendar_start_x, line, curses.color_pair(1))
        else:
            # Current day highlighted
            if calendar_start_y + i < height and calendar_start_x + len(line) <= width:
                x = calendar_start_x
                for j, char in enumerate(line):
                    attr = curses.color_pair(calendar_attrs[i-2][j]) if (i-2) < len(calendar_attrs) and j < len(calendar_attrs[i-2]) else curses.color_pair(1)
                    if x < width:
                        stdscr.addch(calendar_start_y + i, x, char, attr)
                    x += 1

    if calendar_hint_start_y < height and calendar_hint_start_x + len(calendar_hint) <= width:
        stdscr.addstr(calendar_hint_start_y, calendar_hint_start_x, calendar_hint, curses.color_pair(1))

def draw_stopwatch(stdscr, height, width, state):

    if state.stopwatch_running:
        state.total_time = int(time.time() - state.stopwatch_start + state.stopwatch_accumulated)
    else:
        state.total_time = int(state.stopwatch_accumulated)

    # Centralize stopwatch message on terminal
    mode_msg = "Mode: Stopwatch"
    pause_hint = "SPACEBAR : Pause/Resume"
    reset_hint = "R : Reset"

    current_stop_lines = render_stop_timer(state.total_time)

    # Centralize clock and hints on terminal
    center_text(stdscr, current_stop_lines, height, width, curses.color_pair(1), (height - len(current_stop_lines)) // 2)
    center_text(stdscr, [mode_msg], height, width - 1, curses.color_pair(1), (height - len(current_stop_lines)) // 2 - 2)
    center_text(stdscr, [pause_hint], height, width, curses.color_pair(1), (height - len(current_stop_lines)) // 2 + 6)
    center_text(stdscr, [reset_hint], height, width, curses.color_pair(1), (height - len(current_stop_lines)) // 2 + 7)

    return state.stopwatch_accumulated, state.stopwatch_running

def draw_timer(stdscr, height, width, state):

    try:
        if state.timer_input_mode:
            # Exit from text input screen
            def exit_input(ch):
                if ch == 27: # Esc key
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

            # Hint message
            hint_msg = "Enter time in minutes"
            exit_hint = "ESC: Exit"

            # Centralize hints on terminal
            center_text(stdscr, [hint_msg], height, width, curses.color_pair(1), rect_start_y + 3)
            center_text(stdscr, [exit_hint], height, width, curses.color_pair(1), rect_start_y + 4)

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
                    state.timer_input_mode = False
                    curses.curs_set(0)
                    return state.total_time, state.initial_time, state.timer_running, state.timer_input_mode
                state.total_time = int(minutes * 60)
                state.initial_time = state.total_time
                state.timer_running = True
                state.timer_input_mode = False
                curses.curs_set(0)
            except ValueError:
                state.timer_input_mode = False
                curses.curs_set(0)
                return state.total_time, state.initial_time, state.timer_running, state.timer_input_mode
        else:
            # Render timer
            if state.timer_running and state.total_time > 0:
                state.total_time -= 1
            # Timer finished message
            elif state.total_time <= 0 and state.timer_running:
                state.timer_running = False
                stdscr.clear()
                end_msg = "Timer finished!"
                wait_msg = "Returning to clock mode in 5 seconds..."
                center_text(stdscr, [end_msg], height, width, curses.color_pair(1), height // 2)
                center_text(stdscr, [wait_msg], height, width, curses.color_pair(1), height // 2 + 1)
                stdscr.refresh()
                curses.beep()
                time.sleep(5)
            
            current_timer_lines = render_stop_timer(state.total_time)

            mode_msg = "Mode: Timer"
            pause_hint = "SPACEBAR: Pause/Resume"
            reset_hint = "R: Reset"

            # Centralize timer and hints on terminal
            center_text(stdscr, current_timer_lines, height, width, curses.color_pair(1), (height - len(current_timer_lines)) // 2)
            center_text(stdscr, [mode_msg], height, width - 1, curses.color_pair(1), (height - len(current_timer_lines)) // 2 - 2)
            center_text(stdscr, [pause_hint], height, width, curses.color_pair(1), (height - len(current_timer_lines)) // 2 + 6)
            center_text(stdscr, [reset_hint], height, width, curses.color_pair(1), (height - len(current_timer_lines)) // 2 + 7)

        return state.total_time, state.initial_time, state.timer_running, state.timer_input_mode

    except (KeyboardInterrupt, curses.error):
        curses.curs_set(0)
        return state.total_time, state.initial_time, state.timer_running, False
