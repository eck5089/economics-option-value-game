from otree.api import *
import json
import random

from game_config import (
    MAJORS,
    CAREERS,
    STATES,
    EMPIRICAL_FACTS,
    FALLBACK_CODE,
    FALLBACK_LABEL,
    FALLBACK_VALUE,
    offer_probability,
    access_label,
    access_segments,
    realize_offers,
    best_available,
    ex_ante_summary,
    known_state_winners,
)


doc = """
Choosing a Major: a two-round individual classroom game illustrating specialization,
uncertainty, career breadth, and option value.
"""


class C(BaseConstants):
    NAME_IN_URL = 'career_option_value'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 2

    ROUND_FORESIGHT = 1
    ROUND_UNCERTAINTY = 2


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    state_code = models.StringField()
    u_tech_data = models.FloatField()
    u_finance = models.FloatField()
    u_business_consulting = models.FloatField()
    u_government_policy = models.FloatField()
    u_people_human_services = models.FloatField()

    major_choice = models.StringField()
    career_choice = models.StringField()

    p_tech_data = models.FloatField()
    p_finance = models.FloatField()
    p_business_consulting = models.FloatField()
    p_government_policy = models.FloatField()
    p_people_human_services = models.FloatField()

    offer_tech_data = models.BooleanField()
    offer_finance = models.BooleanField()
    offer_business_consulting = models.BooleanField()
    offer_government_policy = models.BooleanField()
    offer_people_human_services = models.BooleanField()

    chosen_career_value = models.IntegerField()
    degree_cost = models.IntegerField()
    net_payoff = models.FloatField()
    best_available_career = models.StringField()
    best_available_net_payoff = models.FloatField()
    chose_payoff_maximizing_career = models.BooleanField()

    counterfactual_json = models.LongStringField()

    econ_attractiveness = models.IntegerField(
        choices=[1, 2, 3, 4, 5, 6, 7],
        min=1,
        max=7,
        widget=widgets.RadioSelectHorizontal,
    )

    concept_check = models.StringField(
        choices=[
            ['always_highest', 'Economics always provides the highest-paying career.'],
            ['lowest_cost', 'Economics has the lowest degree cost.'],
            [
                'option_value',
                'Economics preserves access to several valuable career markets, reducing the risk that few good opportunities are available.',
            ],
            ['guarantee', 'Economics guarantees that every specialized employer will hire you.'],
        ],
        widget=widgets.RadioSelect,
    )
    concept_check_correct = models.BooleanField()

    feature_most_important = models.StringField(
        choices=[
            ['earnings', 'High expected career payoff'],
            ['breadth', 'Access to several different career paths'],
            ['uncertainty', 'Protection against an uncertain future labor market'],
            ['cost', 'Degree cost / effort'],
            ['personal_interest', 'Personal interest in the subject or careers'],
            ['other', 'Something else'],
        ],
        widget=widgets.RadioSelect,
    )
    post_comment = models.LongStringField(blank=True)


def _balanced_state_assignments(n_players):
    """Nearly exact balance across 5 states; exact when n is a multiple of 5."""
    state_codes = list(STATES)
    assignments = []
    while len(assignments) < n_players:
        cycle = state_codes.copy()
        random.shuffle(cycle)
        assignments.extend(cycle)
    assignments = assignments[:n_players]
    random.shuffle(assignments)
    return assignments


def creating_session(subsession):
    players = subsession.get_players()
    balanced = subsession.session.config.get('balanced_states', True)

    if balanced:
        state_assignments = _balanced_state_assignments(len(players))
    else:
        state_assignments = [random.choice(list(STATES)) for _ in players]

    for player, state_code in zip(players, state_assignments):
        player.state_code = state_code
        player.u_tech_data = random.random()
        player.u_finance = random.random()
        player.u_business_consulting = random.random()
        player.u_government_policy = random.random()
        player.u_people_human_services = random.random()


def get_draws(player):
    return {
        'tech_data': player.u_tech_data,
        'finance': player.u_finance,
        'business_consulting': player.u_business_consulting,
        'government_policy': player.u_government_policy,
        'people_human_services': player.u_people_human_services,
    }


def major_choice_choices(player):
    return [[code, data['label']] for code, data in MAJORS.items()]


def career_choice_choices(player):
    choices = []
    for career_code, career in CAREERS.items():
        if getattr(player, f'offer_{career_code}'):
            choices.append([career_code, career['label']])
    choices.append([FALLBACK_CODE, FALLBACK_LABEL])
    return choices


def major_cards(player, state_adjusted=False):
    cards = []
    for major_code, major in MAJORS.items():
        access_rows = []
        for career_code, career in CAREERS.items():
            if state_adjusted:
                p = offer_probability(major_code, career_code, player.state_code)
            else:
                p = major['access'][career_code]
            access_rows.append(
                dict(
                    career_code=career_code,
                    career_label=career['label'],
                    career_icon=career['icon'],
                    probability=p,
                    percent=round(100 * p),
                    access_label=access_label(p),
                    filled=access_segments(p),
                    empty=5 - access_segments(p),
                    filled_segments=[1] * access_segments(p),
                    empty_segments=[1] * (5 - access_segments(p)),
                )
            )
        cards.append(
            dict(
                code=major_code,
                label=major['label'],
                icon=major['icon'],
                cost=major['cost'],
                access_rows=access_rows,
            )
        )
    return cards


def set_realized_offers(player):
    """Called only after major_choice is submitted; stores the entire choice set."""
    draws = get_draws(player)
    probabilities, offers = realize_offers(
        player.major_choice, player.state_code, draws
    )

    player.degree_cost = MAJORS[player.major_choice]['cost']
    for career_code in CAREERS:
        setattr(player, f'p_{career_code}', probabilities[career_code])
        setattr(player, f'offer_{career_code}', offers[career_code])

    chosen_major_best = best_available(
        player.major_choice, player.state_code, draws
    )
    player.best_available_career = chosen_major_best['career_code']
    player.best_available_net_payoff = chosen_major_best['net_payoff']

    counterfactuals = []
    for major_code, major in MAJORS.items():
        result = best_available(major_code, player.state_code, draws)
        career_code = result['career_code']
        career_label = (
            FALLBACK_LABEL
            if career_code == FALLBACK_CODE
            else CAREERS[career_code]['label']
        )
        counterfactuals.append(
            dict(
                major_code=major_code,
                major_label=major['label'],
                major_icon=major['icon'],
                degree_cost=major['cost'],
                best_career_code=career_code,
                best_career_label=career_label,
                gross_value=result['gross_value'],
                net_payoff=result['net_payoff'],
                is_actual_major=(major_code == player.major_choice),
            )
        )
    player.counterfactual_json = json.dumps(counterfactuals)


def finalize_career_choice(player):
    if player.career_choice == FALLBACK_CODE:
        gross = FALLBACK_VALUE
    else:
        gross = CAREERS[player.career_choice]['value']

    player.chosen_career_value = gross
    player.net_payoff = gross - player.degree_cost
    player.chose_payoff_maximizing_career = (
        abs(player.net_payoff - player.best_available_net_payoff) < 1e-9
    )
    player.payoff = cu(player.net_payoff)


def opportunity_rows(player, show_probabilities=False):
    rows = []
    for career_code, career in CAREERS.items():
        p = getattr(player, f'p_{career_code}')
        available = getattr(player, f'offer_{career_code}')
        rows.append(
            dict(
                code=career_code,
                label=career['label'],
                icon=career['icon'],
                value=career['value'],
                probability=p,
                percent=round(100 * p),
                available=available,
                net_if_chosen=career['value'] - player.degree_cost,
                show_probability=show_probabilities,
            )
        )
    return rows


def round_summary(player):
    state = STATES[player.state_code]
    major = MAJORS[player.major_choice]
    career_label = (
        FALLBACK_LABEL
        if player.career_choice == FALLBACK_CODE
        else CAREERS[player.career_choice]['label']
    )
    return dict(
        round_number=player.round_number,
        condition='Foresight' if player.round_number == 1 else 'Uncertainty',
        state_code=player.state_code,
        state_label=state['label'],
        state_icon=state['icon'],
        major_code=player.major_choice,
        major_label=major['label'],
        major_icon=major['icon'],
        career_label=career_label,
        chosen_career_value=player.chosen_career_value,
        degree_cost=player.degree_cost,
        net_payoff=player.net_payoff,
        best_available_net_payoff=player.best_available_net_payoff,
        maximizing=player.chose_payoff_maximizing_career,
        counterfactuals=json.loads(player.counterfactual_json),
    )


class Intro(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.ROUND_FORESIGHT


class BaselineSurvey(Page):
    form_model = 'player'
    form_fields = ['econ_attractiveness']

    @staticmethod
    def is_displayed(player):
        return player.round_number == C.ROUND_FORESIGHT


class MajorOverview(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.ROUND_FORESIGHT

    @staticmethod
    def vars_for_template(player):
        return dict(majors=major_cards(player, state_adjusted=False))


class MajorChoice(Page):
    form_model = 'player'
    form_fields = ['major_choice']
    preserve_unsubmitted_inputs = True

    @staticmethod
    def vars_for_template(player):
        foresight = player.round_number == C.ROUND_FORESIGHT
        state = STATES[player.state_code]
        return dict(
            foresight=foresight,
            uncertainty=not foresight,
            state=state,
            majors=major_cards(player, state_adjusted=foresight),
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        set_realized_offers(player)


class StateReveal(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.ROUND_UNCERTAINTY

    @staticmethod
    def vars_for_template(player):
        return dict(
            state=STATES[player.state_code],
            all_state_labels=[s['label'] for s in STATES.values()],
        )

    @staticmethod
    def js_vars(player):
        return dict(
            actual_state_label=STATES[player.state_code]['label'],
            all_state_labels=[s['label'] for s in STATES.values()],
        )


class JobMarket(Page):
    @staticmethod
    def vars_for_template(player):
        return dict(
            state=STATES[player.state_code],
            major=MAJORS[player.major_choice],
            opportunities=opportunity_rows(player),
            fallback=dict(
                code=FALLBACK_CODE,
                label=FALLBACK_LABEL,
                value=FALLBACK_VALUE,
                net_if_chosen=FALLBACK_VALUE - player.degree_cost,
            ),
        )


class CareerChoice(Page):
    form_model = 'player'
    form_fields = ['career_choice']
    preserve_unsubmitted_inputs = True

    @staticmethod
    def vars_for_template(player):
        return dict(
            state=STATES[player.state_code],
            major=MAJORS[player.major_choice],
            opportunities=opportunity_rows(player),
            fallback=dict(
                code=FALLBACK_CODE,
                label=FALLBACK_LABEL,
                value=FALLBACK_VALUE,
                net_if_chosen=FALLBACK_VALUE - player.degree_cost,
            ),
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        finalize_career_choice(player)


class RoundResult(Page):
    @staticmethod
    def vars_for_template(player):
        return dict(summary=round_summary(player))


class PersonalDebrief(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.ROUND_UNCERTAINTY

    @staticmethod
    def vars_for_template(player):
        p1 = player.in_round(1)
        p2 = player.in_round(2)
        return dict(
            rounds=[round_summary(p1), round_summary(p2)],
        )


class ExAnteReveal(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.ROUND_UNCERTAINTY

    @staticmethod
    def vars_for_template(player):
        rows = []
        for rank, row in enumerate(ex_ante_summary(), start=1):
            row = dict(row)
            row['rank'] = rank
            row['expected_net_payoff_display'] = round(row['expected_net_payoff'], 1)
            row['fallback_percent'] = round(100 * row['probability_fallback'], 1)
            row['specialized_offer_percent'] = round(
                100 * row['probability_any_specialized_offer'], 1
            )
            row['is_economics'] = row['major_code'] == 'economics'
            rows.append(row)
        return dict(rows=rows, winners=known_state_winners())


class ConceptCheck(Page):
    form_model = 'player'
    form_fields = ['concept_check']

    @staticmethod
    def is_displayed(player):
        return player.round_number == C.ROUND_UNCERTAINTY

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.concept_check_correct = player.concept_check == 'option_value'


class ConceptReveal(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.ROUND_UNCERTAINTY


class EmpiricalReveal(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.ROUND_UNCERTAINTY

    @staticmethod
    def vars_for_template(player):
        return dict(empirical_facts=EMPIRICAL_FACTS)


class PostSurvey(Page):
    form_model = 'player'
    form_fields = ['econ_attractiveness', 'feature_most_important', 'post_comment']

    @staticmethod
    def is_displayed(player):
        return player.round_number == C.ROUND_UNCERTAINTY

    @staticmethod
    def vars_for_template(player):
        pre_rating = player.in_round(1).econ_attractiveness
        return dict(pre_rating=pre_rating)


class Final(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.ROUND_UNCERTAINTY

    @staticmethod
    def vars_for_template(player):
        pre = player.in_round(1).econ_attractiveness
        post = player.econ_attractiveness
        return dict(pre=pre, post=post, change=post - pre)


page_sequence = [
    Intro,
    BaselineSurvey,
    MajorOverview,
    MajorChoice,
    StateReveal,
    JobMarket,
    CareerChoice,
    RoundResult,
    PersonalDebrief,
    ExAnteReveal,
    ConceptCheck,
    ConceptReveal,
    EmpiricalReveal,
    PostSurvey,
    Final,
]
