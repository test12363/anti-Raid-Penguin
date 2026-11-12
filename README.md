# 🛡️ Anti-Raid Penguin

A modular, lightweight, and automated Discord security bot built with `discord.py` to protect servers against raids, spam, webhook abuse, and malicious staff actions.

## ✨ Features

* **Anti-Raid (Joins):** Kicks accounts younger than 3 days and blocks mass-join raids (10+ joins within 10 seconds).
* **Anti-Nuke & Staff Protection:** Strips all roles from any staff member who deletes more than 2 channels/roles in 10s, bans more than 5 users in 24h, creates more than 1 webhook in 3h, or grants dangerous permissions (`Administrator`, `Ban`, `Kick`, `Manage Server/Roles`).
* **Auto-Moderation:**
  * **Anti-Links:** Deletes any URL immediately and mutes the user for 30 minutes.
  * **Anti-Mention:** Progressive punishment for `@everyone`/`@here` or >2 mentions per message (1st: Delete, 2nd: Kick, 3rd: Ban).
  * **Anti-Spam:** Deletes messages and applies a 2-hour timeout if a user sends 5 messages within 5 seconds.
  * **Anti-Media & Copy/Paste:** Limits attachments to 1 every 3 seconds and blocks repeated identical messages (5 warnings = auto-blacklist, resets every 24h).
* **Emergency Commands:** `/lockdown` and `/unlock` slash commands restricted to Administrators.

## 🚀 Installation & Setup

1. **Download the repository** (`Code` > `Download ZIP`) and extract it.
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure your bot token:**
   Create a file named `.env` in the root folder and add your token:
   ```env
   DISCORD_TOKEN=your_bot_token_here
   ```
4. **Discord Developer Portal:**
   Enable **Server Members Intent** and **Message Content Intent** under the *Bot* tab.
5. **Server Role Hierarchy:**
   Place the bot's role at the very top of your server's role list (just below the Server Owner) with **Administrator** permission.
6. **Run the bot:**
   ```bash
   python main.py
   ```
