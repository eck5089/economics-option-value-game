# Choosing a Major: Option Value Under Uncertainty

A standalone **oTree** classroom activity about specialization, uncertainty, and the value of keeping career options open.

The activity was designed for Principles of Economics courses and can also be used as an Economics-major recruitment/outreach exercise. Students choose among five stylized college majors, enter an uncertain labor market, observe which career opportunities materialize, and compare realized outcomes with same-state / same-luck counterfactuals.

## What is implemented

- Five majors: Computer Science, Finance, Economics, General Business, Psychology.
- Five specialized career markets plus guaranteed General Employment.
- Fixed degree costs and fixed career values.
- Two rounds:
  1. **Foresight:** the booming labor market is known before the major choice.
  2. **Uncertainty:** the major is chosen before the booming market is revealed.
- One persistent Bernoulli opportunity draw per career market per round.
- Animated sequential reveal of the already-determined opportunity set.
- Career choice from the realized set.
- Same-state / same-luck counterfactuals for all five majors.
- Ex-ante expected-payoff and fallback-risk debrief.
- Option-value concept check and explanation.
- Brief empirical motivation and pre/post Economics-attractiveness question.

## Mechanism in one sentence

Students choose human capital **before** uncertainty is resolved; broader access to several valuable career markets can therefore have option value even when a specialist degree is optimal in a known state.

## Calibration check

The game calibration can be verified without oTree:

```powershell
python validate_mechanism.py
```

The intended known-state winners are:

- Tech & Data Boom → Computer Science
- Finance Boom → Finance
- Business & Consulting Boom → General Business
- Government & Policy Boom → Economics
- People & Human Services Boom → Psychology

Under uncertainty, Economics should rank first in exact expected payoff at approximately **79.67 points**, with approximately **6.9% fallback risk**.

## Run locally

This project is pinned to **oTree 6.0.15** and Python **3.14**.

### Windows / PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
otree devserver
```

Then open:

```text
http://localhost:8000/
```

If `otree` is not recognized, use:

```powershell
python -m otree devserver
```

## Important implementation detail

The JavaScript animations **do not randomize anything**. The server creates and stores the labor-market state and five latent Uniform(0,1) draws. Those stored draws are compared with state- and major-specific offer probabilities. Refreshing the animation page therefore cannot change the participant's opportunity set.

The same latent draws are reused for all five major counterfactuals within a round. This holds the participant's labor-market luck fixed while changing only the major.

## State assignment

`settings.py` currently uses `balanced_states=True`. Within each round, the app assigns states as evenly as possible across participants while randomizing which participant receives each state. Set this to `False` for independent state draws.

## Public room

`settings.py` defines a reusable room named:

```text
econ_options
```

For the public website deployment, use `OTREE_AUTH_LEVEL=STUDY`, create a large `career_option_value` session inside that room, and link visitors directly to the room URL rather than the oTree root/demo page. A room session gives each visitor a separate participant record while preserving one stable public link.

## Main files

- `game_config.py` — canonical degree costs, career values, access matrix, state multipliers, and empirical facts.
- `career_option_value/__init__.py` — oTree models, mechanism logic, pages, and stored variables.
- `career_option_value/*.html` — participant-facing pages.
- `_static/career_option_value/game.css` — visual styling.
- `validate_mechanism.py` — standalone calibration check.
- `DEPLOYMENT.md` — GitHub → Heroku deployment instructions.

## Public use and research use

For the permanent public teaching activity, the recommended setup is:

```text
OTREE_AUTH_LEVEL=STUDY
```

with the reusable `econ_options` room and a pre-created session with ample participant slots.

For a separate controlled classroom/research deployment, also use `STUDY`, but create sessions sized to the actual class or research sample rather than using the large public room session.

Keeping public traffic separate from formal study data is strongly recommended.

## Evidence brief

The game is intentionally stylized. Its qualitative design is motivated by an empirical analysis of 2022–2024 ACS PUMS data combined with BLS occupational projections. A public evidence brief can be linked here once its permanent URL/DOI is available.

## License

Code is released under the [MIT License](LICENSE).
