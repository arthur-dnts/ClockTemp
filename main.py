import requests
import curses
import time
from datetime import datetime

def get_weather():
    url = "https://api.open-meteo.com/v1/forecast?latitude=-7.23072&longitude=-35.8817&current_weather=true"
    try:
        response = requests.get(url)
        return response.json()["current_weather"]["temperature"]
    except requests.RequestException as e:
        return f"Erro: {e}"

numbers = [
    [1,1,1,1,0,1,1,0,1,1,0,1,1,1,1],  # 0
    [0,0,1,0,0,1,0,0,1,0,0,1,0,0,1],  # 1
    [1,1,1,0,0,1,1,1,1,1,0,0,1,1,1],  # 2
    [1,1,1,0,0,1,1,1,1,0,0,1,1,1,1],  # 3
    [1,0,1,1,0,1,1,1,1,0,0,1,0,0,1],  # 4
    [1,1,1,1,0,0,1,1,1,0,0,1,1,1,1],  # 5
    [1,1,1,1,0,0,1,1,1,1,0,1,1,1,1],  # 6
    [1,1,1,0,0,1,0,0,1,0,0,1,0,0,1],  # 7
    [1,1,1,1,0,1,1,1,1,1,0,1,1,1,1],  # 8
    [1,1,1,1,0,1,1,1,1,0,0,1,1,1,1],  # 9 
    [0,0,0,0,1,0,0,0,0,0,1,0,0,0,0],  # :
    [0,0,0,0,0,0,1,1,1,0,0,0,0,0,0],  # -
    [0,0,0,0,0,0,0,0,0,0,0,0,0,1,0],  # .
    [1,1,1,1,0,0,1,0,0,1,0,0,1,1,1],  # C
    [1,1,1,1,0,0,1,1,0,1,0,0,1,0,0],  # F
]

def render_digit(digit_matrix):
    lines = [""] * 5
    for i in range(15):
        row = i // 3
        column = i % 3
        if digit_matrix[i] == 1:
            lines[row] += "██"
        else:
            lines[row] += "  "
    return lines

def render_time():
    current_time = time.strftime("%H:%M:%S")
    lines = [""] * 5
    for char in current_time:
        if char == ":":
            digit_matrix = numbers[10]
        else:
            digit_matrix = numbers[int(char)]
        digit_lines = render_digit(digit_matrix)
        for row in range(5):
            lines[row] += digit_lines[row] + " "
    return lines

def render_temp():
    temp_format = "c"
    current_temp = get_weather()
    temp_str = f"{current_temp:.1f}"
    lines = [""] * 5
    for char in temp_str:
        if char == ".":
            digit_matrix = numbers[12]
        else:
            digit_matrix = numbers[int(char)]
        digit_lines = render_digit(digit_matrix)
        for row in range(5):
            lines[row] += digit_lines[row] + " "
    if temp_format == "c":
        digit_matrix = numbers[13]
    elif temp_format == "f":
        digit_matrix = numbers[14]
    digit_lines = render_digit(digit_matrix)
    for row in range(5):
        lines[row] += digit_lines[row] + " "
    return lines

def main(stdscr):
    curses.curs_set(0)  # Remove cursor
    stdscr.timeout(1000)  # 1 second tick

    last_time = ""
    last_temp = ""

    while True:
        # Get terminal size
        height, width = stdscr.getmaxyx()

        # Date
        current_date = datetime.today().strftime("%d/%m/%Y")

        date_height = len(current_date)
        date_width = len(current_date[0])

        date_start_y = (height - date_height) // 2
        date_start_x = (width - date_width) // 2

        # Clock
        current_time_lines = render_time()
        
        clock_height = len(current_time_lines)
        clock_width = len(current_time_lines[0])

        clock_start_y = (height - clock_height) // 2
        clock_start_x = (width - clock_width) // 2

        # Weather
        current_temp_lines = render_temp()

        temp_height = len(current_temp_lines)
        temp_width = len(current_temp_lines[0])

        temp_start_y = (height - temp_height) // 2 - 6
        temp_start_x = (width - temp_width) // 2

        if "\n".join(current_time_lines) != last_time:
            for i, line in enumerate(current_time_lines):
                stdscr.addstr(clock_start_y + i, clock_start_x, line)
            last_time = "\n".join(current_time_lines)
            stdscr.addstr(date_start_y + 9, date_start_x, current_date)
        
        if "\n".join(current_temp_lines) != last_temp:
            for i, line in enumerate(current_temp_lines):
                stdscr.addstr(temp_start_y + i, temp_start_x, line)
            last_temp = "\n".join(current_temp_lines)

        # Refresh terminal
        stdscr.refresh()

        # Close TUI pressing 'q'
        key = stdscr.getch()
        if key == ord('q'):
            break

curses.wrapper(main)
