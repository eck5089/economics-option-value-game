from os import environ

SESSION_CONFIGS = [
    dict(
        name='career_option_value',
        display_name='Choosing a Major: Option Value Under Uncertainty',
        num_demo_participants=1,
        app_sequence=['career_option_value'],
        balanced_states=True,
    ),
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00,
    participation_fee=0.00,
    doc='Two-round classroom activity on specialization, uncertainty, and career option value.',
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

LANGUAGE_CODE = 'en'
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True
POINTS_CUSTOM_NAME = 'points'

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """
<p>
This project contains a two-round classroom activity about choosing a college major
when future labor-market conditions are uncertain.
</p>
"""

SECRET_KEY = environ.get('OTREE_SECRET_KEY', 'local-development-key-change-before-production')
