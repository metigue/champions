#!/usr/bin/env python3
from data_manager_json import DataManager
from cogs.command_handler import CommandHandler

def test_rankup_command():
    # Initialize data manager
    data_manager = DataManager()
    
    # Initialize command handler
    command_handler = CommandHandler(data_manager)
    
    # Test the rankup command with "mr negative"
    result = command_handler.get_champion_rankup_info("mr negative")
    print(result)

if __name__ == "__main__":
    test_rankup_command()