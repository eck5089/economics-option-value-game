# Deploying the oTree game from GitHub to Heroku

This repository is set up for a direct **GitHub → Heroku** workflow. oTree Hub / OTAI is not required for deployment.

## 1. Put the project on GitHub

The repository root must be the folder containing:

```text
Procfile
requirements.txt
settings.py
game_config.py
career_option_value/
_static/
```

Do not put those files one directory below the repository root, or Heroku will not detect the app correctly.

## 2. Create the Heroku app

In the Heroku Dashboard:

1. Create a new app.
2. Choose a region.
3. Give the app a memorable name.

## 3. Add PostgreSQL

A public/production oTree deployment should use PostgreSQL rather than the local SQLite database.

Provision **Heroku Postgres**. Heroku automatically supplies the database connection as `DATABASE_URL`.

Do not manually paste database credentials into the repository.

## 4. Add production config vars

In the app's **Settings → Config Vars**, use:

```text
OTREE_PRODUCTION=1
OTREE_AUTH_LEVEL=STUDY
OTREE_ADMIN_PASSWORD=<strong private password>
OTREE_SECRET_KEY=<long random secret>
```

`DATABASE_URL` should already exist after provisioning Heroku Postgres.

The public website deployment uses `STUDY` rather than `DEMO` because visitors enter through a reusable room URL instead of the oTree Demo landing page.

## 5. Connect Heroku to GitHub

In the Heroku app's **Deploy** tab:

1. Choose **GitHub** as the deployment method.
2. Authenticate Heroku with GitHub if prompted.
3. Connect this repository.
4. Select the `main` branch.
5. Use **Manual Deploy** for the first deployment.

After the first successful deployment, automatic deploys from `main` can be enabled if desired.

## 6. Initialize the oTree database

After the first successful build and after PostgreSQL is attached, initialize the database once:

```text
otree resetdb
```

For Cedar-generation Heroku apps this can usually be run from the Dashboard under **More → Run console**.

Important: `resetdb` deletes existing oTree data. It is appropriate for initial setup and deliberate fresh starts, not as a routine deployment command once real data exist.

## 7. Create the public room session

`settings.py` defines a reusable room:

```text
econ_options
```

After deployment:

1. Open the oTree admin interface.
2. Go to **Rooms**.
3. Open **Choosing a Major: Option Value Under Uncertainty** (`econ_options`).
4. Create a `career_option_value` session with a generous number of participant slots (for example 250 for the public demo).

Each visitor receives a separate participant slot and therefore their own game experience. When the room session fills, create a new session in the same room; the public room URL remains stable.

For a formal classroom/research run, use a separate deployment or separate controlled room/session sized to the intended sample so public visitors do not enter the study data.

## 8. Link directly to the room from the website

Do not link the public website to the Heroku root page or to a temporary demo/session link.

Use the reusable room URL, for example:

```text
https://YOUR-APP-NAME.herokuapp.com/room/econ_options/?welcome_page_ok=1
```

The `welcome_page_ok=1` parameter is intended to allow the participant to proceed directly through the room entry flow. Test the exact URL in an incognito/private browser before publishing it.

Recommended website structure:

```text
Why Economics Keeps Options Open

[Play the interactive activity]
[Read the evidence brief]
[View source / teaching materials]
```

The first link should point to the room URL above. The evidence brief can live on the project website, an institutional repository, or Zenodo. The source link can point to this GitHub repository.

## Files Heroku uses

- `requirements.txt` installs `otree==6.0.15` and the PostgreSQL driver.
- `.python-version` requests Python 3.14.
- `Procfile` starts the production server using Heroku's assigned `$PORT`:

```text
web: otree prodserver $PORT
```

- `settings.py` reads production secrets from environment variables and defines the reusable `econ_options` room.

## Updating the deployed app later

If automatic GitHub deploys are enabled:

```bash
git add .
git commit -m "Describe the change"
git push
```

Heroku then builds and deploys the new commit automatically.

Do not run `otree resetdb` simply because code changed. Doing so would erase collected data.
