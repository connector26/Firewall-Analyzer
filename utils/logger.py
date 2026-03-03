import logging
from pathlib import Path

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Logger setup
logger = logging.getLogger("FirewallAnalyzer")
logger.setLevel(logging.DEBUG)  # Can be set to INFO in production

# Console Handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# File Handler
file_handler = logging.FileHandler(log_dir / "firewall_analyzer.log", mode="a")
file_handler.setLevel(logging.DEBUG)

# Formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add Handlers
if not logger.handlers:  # Prevent duplicate handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
