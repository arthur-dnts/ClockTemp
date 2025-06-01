"""
# cal.py - Copyright (c) 2025 Arthur Dantas
# This file is part of ClockTemp, licensed under the GNU General Public License v3.
# See <https://www.gnu.org/licenses/> for details.
"""

import calendar
from datetime import datetime

def render_calendar(year=None, month=None):
    now = datetime.now()
    if year is None:
        year = now.year
    if month is None:
        month = now.month
    
    calendar.setfirstweekday(calendar.SUNDAY) # Set first day of the week to Sunday

    # Adjust month and year if out of range
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1
    
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    header = f"{month_name} {year}"
    lines = [header.center(20)]
    lines.append("Su Mo Tu We Th Fr Sa") # Weekday header

    # Lists to stores lines and attributes
    formatted_lines = []
    attributes = []
    
    current_day = now.day if year == now.year and month == now.month else None

    for week in cal:
        week_str = ""
        week_attrs = []
        for day in week:
            if day == 0:
                week_str += "   "
                week_attrs.extend([0, 0, 0])
            else:
                week_str += f"{day:02} "
                if day == current_day:
                    week_attrs.extend([2, 2, 1])  # Highlight only for 2 digits of current day
                else:
                    week_attrs.extend([1, 1, 1])  # All characters are normal
        formatted_lines.append(week_str.rstrip())
        attributes.append(week_attrs)

    return lines + formatted_lines, attributes
