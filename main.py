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
    [0,1,0,0,1,0,0,1,0,0,1,0,0,1,0],  # 1
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

def main(stdscr):
    curses.curs_set(0)  # Remove cursor
    stdscr.timeout(1000)  # 1 second tick

    last_time = ""
    last_temp_update = 0
    current_temp = "N/A"

    while True:
        start_time = time.time()

        # Refresh temperature
        if time.time() - last_temp_update >= 600:
            current_temp = get_weather()
            last_temp_update = time.time()

        # Get terminal size
        height, width = stdscr.getmaxyx()

        # Date and Temperature
        current_date = datetime.today().strftime("%d/%m/%Y")
        dateTemp = f"{current_date} | {current_temp:.1f} ºC" if isinstance(current_temp, (int, float)) else f"{current_date} | {current_temp}"

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

        # 1 second for each interaction
        elapsed_time = time.time() - start_time
        sleep_time = max(0, 1.0 - elapsed_time)
        time.sleep(sleep_time)

curses.wrapper(main)
