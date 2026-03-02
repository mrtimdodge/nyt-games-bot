# NYT Games Discord Bot

A Discord bot that tracks **Wordle**, **Connections**, **Strands**, and **Pips** scores and maintains server leaderboards.

Just paste your game results into Discord and the bot records them automatically. Leaderboards update in real time and a monthly summary is posted automatically at the end of each month.

---

## Games Supported

| Game | Emoji |
|------|-------|
| Wordle | 🟩 🟨 ⬜ |
| Connections | 🟨 🟩 🟦 🟪 |
| Strands | 🔵 💡 🟡 |
| Pips | 🍪 |

---

## Commands

| Command | Description |
|---------|-------------|
| `?ranks [today\|week\|month\|10-day\|all-time\|<puzzle #>\|<MM/DD/YYYY>]` | Leaderboard for the given period. Defaults to this week. |
| `?ranks all [<period>]` | Show leaderboards for all games at once. |
| `?missing [<puzzle #>]` | List players who haven't submitted. Defaults to today. |
| `?entries [<player>]` | List all recorded entries for a player. Defaults to you. |
| `?stats [<player1> <player2> ...]` | Show stats for one or more players. Defaults to you. |
| `?view [<player>] <puzzle #> [...]` | View specific puzzle entries for a player. |
| `?help [<command>]` | Show help for all commands or a specific one. |

### Admin Commands

| Command | Description |
|---------|-------------|
| `?add [<player>] <puzzle output>` | Manually add an entry. |
| `?remove [<player>] <puzzle #>` | Remove an entry. |

> **Tip:** You don't need `?add` — just paste your game result directly in the channel and the bot records it. It will react with ✅ on success or ❌ if something went wrong.

---

## Special Events

- **Wordle in 2** — bot posts a celebratory GIF
- **Wordle in 1** — bot pings @everyone with a GIF
- **Pips triple cookie** — bot posts a Cookie Monster GIF
- **End of month** — bot automatically posts final monthly leaderboards for all games at 11pm EST on the last day of the month

---

## Setup

### 1. Environment Variables

Copy `.env_docker` to `.env` and fill in your values:

```env
DISCORD_TOKEN=your_token_here
GUILD_ID=your_guild_id
DISCORD_ENV=production

# One block per game (wordle / connections / strands / pips)
WORDLE_MYSQL_HOST=localhost
WORDLE_MYSQL_USER=root
WORDLE_MYSQL_PASS=password
WORDLE_MYSQL_DB_NAME=nyt_wordle

CONNECTIONS_MYSQL_HOST=localhost
CONNECTIONS_MYSQL_USER=root
CONNECTIONS_MYSQL_PASS=password
CONNECTIONS_MYSQL_DB_NAME=nyt_connections

STRANDS_MYSQL_HOST=localhost
STRANDS_MYSQL_USER=root
STRANDS_MYSQL_PASS=password
STRANDS_MYSQL_DB_NAME=nyt_strands

PIPS_MYSQL_HOST=localhost
PIPS_MYSQL_USER=root
PIPS_MYSQL_PASS=password
PIPS_MYSQL_DB_NAME=nyt_pips

# Optional
GIPHY_API_KEY=your_giphy_key       # enables celebratory GIFs
CONFIRM_ENTRIES=True                # react ✅/❌ to submissions
NYT_GAMES_CHANNEL=channel_id       # post all games to one channel instead of per-game channels

# Pips scoring tuning
MAX_TIME_MULTIPLIER=12.0
MIN_SCORE_FOR_COMPLETION=10.0
EASY_MULTIPLIER=1.0
MEDIUM_MULTIPLIER=1.5
HARD_MULTIPLIER=2.0
```

### 2. Database

Run `scripts/setup.sql` against your MySQL server to create the required databases and tables.

### 3. Run with Docker

```bash
docker build -t nyt-games-bot .
docker run --env-file .env nyt-games-bot
```

### 4. Run locally

```bash
pip install -r requirements.txt
python bot.py
```

---

## Channel Routing

The bot uses the Discord channel name to determine which game to handle.

- If a channel name contains `wordle`, `connections`, `strands`, or `pips`, commands and submissions in that channel are automatically routed to the right game.
- If posting in a general channel, prefix commands with the game name (e.g. `?ranks wordle`).
- Set `NYT_GAMES_CHANNEL` to post all automated messages (like monthly results) to a single shared channel.
