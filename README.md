# 🎬 Instagram Reel Chat Sender

A Selenium-based automation script that logs into Instagram 🔐 and sends a Reel link 🎥 (with an optional message 💬) via DM to a list of target usernames 👥.

## ⚠️ Disclaimer

This script is for **personal/educational use only** 🎓. Automating actions on Instagram violates Instagram's Terms of Service and can result in your account being rate-limited, flagged, or permanently banned 🚫. Use responsibly:

- 🙅 Don't spam people who haven't agreed to receive messages.
- ⏱️ Add realistic delays between actions (already built in).
- 💀 Don't run this on an account you can't afford to lose.
- 🧑‍⚖️ You are solely responsible for how you use this script.

## ✨ Features

- 🤖 Automated Chrome login via Selenium + `webdriver-manager`
- ⌨️ Human-like typing delays and randomized wait times to reduce detection risk
- ❌ Dismisses common post-login popups ("Save Login Info", "Turn on Notifications")
- 📩 Opens a DM thread with each target user and sends a Reel link + message
- 📊 Per-user status tracking (`sent`, `failed`, `not found`) with a summary printed at the end
- 🕶️ Optional headless mode

## 🧰 Requirements

- 🐍 Python 3.8+
- 🌐 Google Chrome installed
- 📦 Python packages:
  ```bash
  pip install selenium webdriver-manager
  ```

## 🛠️ Setup

1. 📥 Clone or download this script (`instagram_reel_sender.py`).
2. 📦 Install dependencies:
   ```bash
   pip install selenium webdriver-manager
   ```
3. ✏️ Open the script and edit the `Config` block at the bottom (or in the `Config` dataclass) with your details:

   ```python
   cfg = Config(
       username  = "your_instagram_username",
       password  = "your_instagram_password",
       reel_url  = "https://www.instagram.com/reel/XXXXXXXXXXX/",
       message   = "Check this out! 🔥",
       targets   = ["target_username_1", "target_username_2"],
       headless  = False,
   )
   ```

   > 💡 **Tip:** Avoid hardcoding credentials directly in the file, especially if you plan to share or version-control it. Consider loading `username`/`password` from environment variables or a `.env` file instead.

## 🚀 Usage

Run the script:

```bash
python instagram_reel_sender.py
```

What happens:

1. 🌐 Chrome launches (visible unless `headless=True`) and navigates to the Instagram login page.
2. ⌨️ Credentials are entered with human-like typing delays.
3. ❌ Post-login popups are dismissed automatically.
4. 🔎 For each target in `targets`, the script opens a new DM, searches for the user, opens the chat, and sends the Reel link + message.
5. ⏳ A randomized delay is applied between each user to reduce the chance of being flagged.
6. ✅ A summary of results (sent/failed/not found) is printed at the end, and the browser closes.

## ⚙️ Configuration Reference

| Field | Description | Default |
|---|---|---|
| 👤 `username` | Your Instagram username | `"your_instagram_username"` |
| 🔑 `password` | Your Instagram password | `"your_instagram_password"` |
| 🎥 `reel_url` | The Reel link to send | placeholder URL |
| 💬 `message` | Text sent alongside the Reel link | `"Check this out! 🔥"` |
| 👥 `targets` | List of usernames to DM | example list |
| ⏱️ `delay_between_actions` | Random delay range (sec) between UI actions | `(2, 4)` |
| ⏳ `delay_between_users` | Random delay range (sec) between sending to different users | `(8, 15)` |
| 🕶️ `headless` | Run Chrome without a visible window | `False` |

## 🐞 Known Limitations

- 🧩 Relies on Instagram's current DOM structure (XPath selectors); UI changes on Instagram's end can break the script and require selector updates.
- 🔐 No built-in handling for 2FA challenges, CAPTCHAs, or "suspicious login" checkpoints — these will need manual intervention if triggered.
- 🍪 No persistent session/cookie storage, so it logs in fresh every run.
- 🎯 Selector for finding a user in search results (`//span[contains(text(),'{target_username}')]`) can occasionally match the wrong element if usernames overlap with other visible text.

## 📝 Logging

The script logs progress and errors to stdout using Python's `logging` module 🪵, including a final summary table 📊 of DM results per target user.

## 📄 License

Provided as-is for personal/educational use 🎓. No warranty of any kind.
