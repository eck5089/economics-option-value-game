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

A simple Windows workflow is GitHub Desktop:

1. Create a new GitHub repository (for example `economics-option-value-game`).
2. Add this folder as the local repository.
3. Commit all files.
4. Publish/push the `main` branch to GitHub.

Command-line equivalent:

```bash
git init
git add .
git commit -m "Initial public version"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/economics-option-value-game.git
git push -u origin main
```

## 2. Create the Heroku app

In the Heroku Dashboard:

1. Create a new app.
2. Choose a region.
3. Give the app a memorable name, e.g. `economics-option-value-game` if available.

Heroku will give it a public URL such as:

```text
https://YOUR-APP-NAME.herokuapp.com/
```

## 3. Add PostgreSQL

A public/production oTree deployment should use PostgreSQL rather than the local SQLite database.

In the Heroku app, provision **Heroku Postgres** (the smallest/cheapest plan is sufficient for a small classroom demo).

Heroku automatically supplies the database connection as:

```text
DATABASE_URL
```

Do not manually paste database credentials into the repository.

## 4. Add production config vars

In the app's **Settings → Config Vars**, set:

```text
OTREE_PRODUCTION=1
OTREE_AUTH_LEVEL=DEMO
OTREE_ADMIN_PASSWORD=<strong private password>
OTREE_SECRET_KEY=<long random secret>
```

For a controlled classroom/research deployment, use:

```text
OTREE_AUTH_LEVEL=STUDY
```

instead of `DEMO`.

`DATABASE_URL` should already exist after provisioning Heroku Postgres.

## 5. Connect Heroku to GitHub

In the Heroku app's **Deploy** tab:

1. Choose **GitHub** as the deployment method.
2. Authenticate Heroku with GitHub if prompted.
3. Search for and connect this repository.
4. Select the `main` branch.
5. Use **Manual Deploy** for the first deployment.

After the first successful deployment, you can enable automatic deploys from `main` if desired. Then every push to GitHub will rebuild and deploy the app automatically.

## 6. Initialize the oTree database

After the first successful build and after PostgreSQL is attached, initialize the database once:

```text
otree resetdb
```

For Cedar-generation Heroku apps this can usually be run from the Dashboard under **More → Run console**.

Alternatively, with the Heroku CLI:

```bash
heroku run otree resetdb -a YOUR-APP-NAME
```

Important: `resetdb` deletes existing oTree data. It is appropriate for the initial setup and for deliberate fresh starts, not as a routine deployment command once you are collecting real data.

## 7. Open and test the public site

Open the Heroku app URL in an incognito/private browser window.

With:

```text
OTREE_AUTH_LEVEL=DEMO
```

visitors should be able to play the public demo without access to the full admin interface.

Test the full participant flow at least once before linking it publicly.

## 8. Link from your website

Recommended public-facing structure:

```text
Why Economics Keeps Options Open

[Play the interactive activity]
[Read the evidence brief]
[View source / teaching materials]
```

The first link goes to the Heroku public demo URL. The evidence brief can live on your website, institutional repository, or Zenodo. The source link can point back to this GitHub repository.

## Recommended two-deployment structure

Use the same GitHub repository for two separate Heroku apps:

### Public demo

```text
OTREE_AUTH_LEVEL=DEMO
```

Permanent website link; no formal research data collection.

### Classroom/research

```text
OTREE_AUTH_LEVEL=STUDY
```

Controlled sessions/rooms and clean study data.

This keeps random public visitors out of classroom/research data.

## Files Heroku uses

- `requirements.txt` installs `otree==6.0.15`.
- `.python-version` requests the latest supported Python 3.14 patch release.
- `Procfile` starts the production server using Heroku's assigned `$PORT`:

```text
web: otree prodserver $PORT
```

- `settings.py` reads production secrets from environment variables.

## Updating the deployed app later

If automatic GitHub deploys are enabled:

```bash
git add .
git commit -m "Describe the change"
git push
```

Heroku then builds and deploys the new commit automatically.

Do not run `otree resetdb` simply because code changed. Doing so would erase collected data.
