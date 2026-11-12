# --- ANTI-RAID SETTINGS (JOINS) ---
MAX_JOINS = 10              # Max 10 joins...
JOIN_WINDOW = 10            # ...within 10 seconds
MIN_ACCOUNT_AGE_DAYS = 3    # Minimum account age: 3 days

# --- AUTOMOD SETTINGS (MESSAGES) ---
MAX_MESSAGES_ALLOWED = 4    # Max 4 messages in 5 sec (punished on 5th)
MESSAGE_WINDOW = 5          # 5 seconds window
SPAM_MUTE_HOURS = 2         # Spam timeout: 2 hours
LINK_MUTE_MINUTES = 30      # Link timeout: 30 minutes
IMAGE_WINDOW = 3            # Max 1 image/file every 3 seconds
MAX_WARNINGS = 5            # 5 warnings = Blacklist (Ban)

# --- ANTI-NUKE SETTINGS (STAFF / SERVER) ---
NUKE_LIMIT = 2              # Max 2 deletions (channels or roles)...
NUKE_WINDOW = 10            # ...within 10 seconds
BAN_LIMIT = 5               # Max 5 bans...
BAN_WINDOW = 86400          # ...within 24 hours (86400 seconds)
WEBHOOK_LIMIT = 1           # Max 1 webhook...
WEBHOOK_WINDOW = 10800      # ...within 3 hours (10800 seconds)
