"""Entry point for the Briefing System."""
import os
from dotenv import load_dotenv

from storage.json_storage import JsonPreferencesStorage

def main() -> None:
    """Initializes dependencies and starts the application."""
    load_dotenv()
    
    # 1. Initialize infrastructure
    storage = JsonPreferencesStorage()
    
    # Placeholder for future services
    print("Briefy System initialized successfully.")
    
    # 2. Inject dependencies (to be done when team finishes modules)
    # bot = DiscordBotManager(storage=storage, ...)
    # bot.start()

if __name__ == "__main__":
    main()