import time

# Numbers matrix 5x3
NUMBERS = [
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
]

# Render digits from NUMBERS
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

# Render time based on current time
def render_time(timeFormat):
    current_time = time.strftime(timeFormat)
    lines = [""] * 5
    for char in current_time:
        if char == ":":
            digit_matrix = NUMBERS[10]
        else:
            digit_matrix = NUMBERS[int(char)]
        digit_lines = render_digit(digit_matrix)
        for row in range(5):
            lines[row] += digit_lines[row] + " "
    return lines
