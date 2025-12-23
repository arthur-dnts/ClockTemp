"""
# clock.py - Copyright (c) 2025 Arthur Dantas
# This file is part of ClockTemp, licensed under the GNU General Public License v3.
# See <https://www.gnu.org/licenses/> for details.
"""

import time

"""
Copyright (c) 2009-2018 tty-clock contributors
Copyright (c) 2008-2009 Martin Duquesnoy <xorg62@gmail.com>
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright
  notice, this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above
  copyright notice, this list of conditions and the following disclaimer in the
  documentation and/or other materials provided with the distribution.
* Neither the name of the tty-clock nor the names of its
  contributors may be used to endorse or promote products derived from this
  software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

# Matrix of numbers adapted from tty-clock
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
        if digit_matrix[i] == 1:
            lines[row] += "██"
        else:
            lines[row] += "  "
    return lines

# Format clock time based on given format
def format_clock(time_obj, format):
    return time_obj.strftime(format)

# Format total seconds into HH:MM:SS for stopwatch and timer
def format_time(total_seconds):
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"

# Render digits for clock, stopwatch and timer
def render_digits(time_str):
    lines = [""] * 5
    for char in time_str:
        if char == ":":
            digit_matrix = NUMBERS[10]
        else:
            digit_matrix = NUMBERS[int(char)]
        digit_lines = render_digit(digit_matrix)
        for row in range(5):
            lines[row] += digit_lines[row] + " "
    return lines
