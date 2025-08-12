#!/usr/bin/env python3
"""
Setup script for configuring the Telegram bot token.
"""

import os
import sys

def main():
    print("🤖 Mini Dungeon Master Bot Token Setup 🤖")
    print("=" * 50)
    
    # Check if token is already set
    current_token = os.getenv('TELEGRAM_TOKEN', '')
    if current_token and current_token != 'your_telegram_bot_token_here':
        print(f"✅ Token already set: {current_token[:10]}...")
        return
    
    print("❌ No valid Telegram bot token found!")
    print("\nTo fix this issue, you need to:")
    print("\n1. Get your bot token from @BotFather on Telegram")
    print("2. Set the environment variable using one of these methods:")
    print("\n   Method 1 - Export for current session:")
    print("   export TELEGRAM_TOKEN=your_actual_bot_token_here")
    print("\n   Method 2 - Add to your shell profile (~/.bashrc, ~/.zshrc, etc.):")
    print("   echo 'export TELEGRAM_TOKEN=your_actual_bot_token_here' >> ~/.bashrc")
    print("   source ~/.bashrc")
    print("\n   Method 3 - Set temporarily and run:")
    print("   TELEGRAM_TOKEN=your_actual_bot_token_here python3 bot.py")
    print("\n⚠️  IMPORTANT: Replace 'your_actual_bot_token_here' with your real token!")
    print("   Do NOT include quotes around the token value.")
    
    # Ask if user wants to set it now
    try:
        response = input("\nWould you like to set the token now? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            token = input("Enter your Telegram bot token: ").strip()
            if token and token != 'your_telegram_bot_token_here':
                os.environ['TELEGRAM_TOKEN'] = token
                print(f"✅ Token set for this session: {token[:10]}...")
                print("You can now run: python3 bot.py")
            else:
                print("❌ Invalid token provided!")
        else:
            print("Please set the token manually and try again.")
    except KeyboardInterrupt:
        print("\n\nSetup cancelled. Please set the token manually.")
        sys.exit(1)

if __name__ == "__main__":
    main()