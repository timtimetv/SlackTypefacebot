# 🔤 Typeface of the Day

A Slack bot that posts one typeface a day, every day of the year, with a fun fact. It posts at **9:00am Toronto time** and runs free on GitHub Actions.

- `typefaces.json`: 366 typefaces, one per calendar date (Feb 29 included).
- `bot.py`: picks today's typeface and posts it to Slack. Uses only the Python standard library.
- `.github/workflows/daily-typeface.yml`: the daily schedule.

## Setup (about 10 minutes)

### 1. Connect it to a Slack channel
1. Go to https://api.slack.com/apps → **Create New App** → **From scratch**. Name it "Typeface of the Day" and pick your workspace.
2. In the sidebar, open **Incoming Webhooks** and switch it **On**.
3. Click **Add New Webhook to Workspace**, choose the channel, and click **Allow**.
4. Copy the webhook URL (`https://hooks.slack.com/services/...`). Treat it like a password.

Optional: under **Basic Information → Display Information**, give the bot an icon and colour.

### 2. Put the code on GitHub
1. Create a new repository at https://github.com/new. It can be private.
2. Upload these files. Keep the `.github/workflows/` folder structure exactly as it is.

### 3. Add the webhook as a secret
In the repo, go to **Settings → Secrets and variables → Actions → New repository secret**:
- Name: `SLACK_WEBHOOK_URL`
- Value: the webhook URL from step 1

### 4. Send a test post
Go to **Actions → Daily Typeface → Run workflow**, keep "force" ticked, and click **Run workflow**. Today's typeface should show up in your channel within a minute.

After that it posts automatically every morning.

## Local commands

```bash
python3 bot.py --validate                              # check the data file
python3 bot.py --dry-run --force                       # preview today's message
python3 bot.py --dry-run --force --date 2026-12-25     # preview any date
SLACK_WEBHOOK_URL=https://hooks.slack.com/... python3 bot.py --force   # post now
```

## Notes
- **Time zone:** set by `BOT_TIMEZONE` (default `America/Toronto`) and `BOT_POST_HOUR` (default `9`). If you change the time zone, also change the two UTC cron times in the workflow so one of them falls in your 9am hour.
- **Timing:** GitHub's scheduler can run a few minutes late when it's busy, so expect the post around 9:00–9:15.
- **Keep-alive:** GitHub pauses scheduled workflows in repos with no activity for 60 days. If that happens, re-enable it from the Actions tab, or push a small commit every couple of months.
- **Editing facts:** edit `typefaces.json`. Entry 1 is Jan 1, entry 60 is Feb 29, and entry 366 is Dec 31. Run `--validate` afterwards.
