#!/usr/bin/env python3
"""
Test script to check the new rankup formatting
"""

from champion_model import Champion
from data_manager_json import DataManager
from cogs.command_handler import CommandHandler

# Load the data manager
data_manager = DataManager()

# Initialize command handler with data manager
command_handler = CommandHandler(data_manager)

# Test champion rankup output for Spider-Ham
print('Testing Spider-Ham:')
result = command_handler.get_champion_rankup_info('Spider-Ham')
print(result)
print()

print('='*50)
print()

# Also test Guardian
print('Testing Guardian:')
result2 = command_handler.get_champion_rankup_info('Guardian')
print(result2)
print()

print('='*50)
print()

# Also test White Tiger
print('Testing White Tiger:')
result3 = command_handler.get_champion_rankup_info('White Tiger')
print(result3)
print()

print('='*50)
print()

# Test a champion with ranking and battlegrounds rating
print('Testing a champion with both ranking and BG rating:')
result4 = command_handler.get_champion_rankup_info('Karolina Dean')
print(result4)