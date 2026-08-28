"""Run this with ordinary Python to verify the canonical calibration.

No oTree installation is required for this file.
"""
from game_config import ex_ante_summary, known_state_winners

EXPECTED_WINNERS = {
    'tech_boom': 'Computer Science',
    'finance_boom': 'Finance',
    'business_boom': 'General Business',
    'policy_boom': 'Economics',
    'people_boom': 'Psychology',
}

print('\nKNOWN-STATE WINNERS')
print('-' * 72)
for row in known_state_winners():
    expected = EXPECTED_WINNERS[row['state_code']]
    ok = row['major_label'] == expected
    print(
        f"{row['state_label']:<34} -> {row['major_label']:<18} "
        f"E[payoff]={row['expected_net_payoff']:.3f}  {'OK' if ok else 'CHECK'}"
    )
    assert ok

print('\nEX ANTE OUTCOMES UNDER UNCERTAINTY')
print('-' * 92)
rows = ex_ante_summary()
for rank, row in enumerate(rows, 1):
    print(
        f"{rank}. {row['major_label']:<18} "
        f"E[payoff]={row['expected_net_payoff']:>7.3f}  "
        f"P(fallback)={100*row['probability_fallback']:>5.1f}%  "
        f"E[specialized offers]={row['expected_number_specialized_offers']:.3f}"
    )

assert rows[0]['major_code'] == 'economics'
print('\nPASS: Economics is the unique ex-ante expected-payoff winner, and each major wins its intended known state.')
