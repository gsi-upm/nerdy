#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""lists.py: Lists of words that will be useful for tagging."""

__author__ = "Rami Al-Rfou"
__email__ = "rmyeid gmail"

WEEK_DAYS = {'Sunday', 'Sun.', 'Monday', 'Mon.', 'Tuesday', 'Tu.', 'Tue.',
             'Tues.', 'Wednesday', 'Wed.', 'Thursday', 'Th.', 'Thu.', 'Thur.',
              'Thurs.', 'Friday', 'Fri.', 'Saturday', 'Sat.'}

MONTHS = {
'January', 'Jan.', 'February', 'Feb.', 'March', 'Mar.', 'April', 'Apr.', 'May',
'June', 'Jun.', 'July', 'Jul.', 'August', 'Aug.', 'September', 'Sep.', 'Sept.',
'October', 'Oct.', 'November', 'Nov.', 'December', 'Dec.'}

WEEK_MONTHS = set(MONTHS).union(WEEK_DAYS)

CAPITALS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    
NUMERALS = {"one", "two", "three", "four", "five", "six", "seven", "eight",
            "nine", "ten", "thousand", "million", "billion", "trillion"}
