#!/usr/bin/env python3
"""
Test script to verify the new weighting normalization works correctly
"""

def test_weight_normalization():
    """Test that weights are properly normalized"""

    # Test Case 1: Equal weights (should each be 1/6 ≈ 0.167)
    print("Test Case 1: Equal weights")
    preferences = {
        'offensive_weight': 0.17,
        'defensive_weight': 0.17,
        'longevity_weight': 0.17,
        'team_success_weight': 0.17,
        'efficiency_weight': 0.16,
        'peak_performance_weight': 0.16
    }

    total_weight = sum(preferences.values())
    print(f"  Total weight: {total_weight}")

    normalized = {k: v / total_weight for k, v in preferences.items()}
    print(f"  Normalized weights sum: {sum(normalized.values())}")
    for k, v in normalized.items():
        print(f"    {k}: {v:.3f} ({v*100:.1f}%)")

    # Test Case 2: Emphasis on offense (50%) and team success (30%)
    print("\nTest Case 2: Offense 50%, Team Success 30%, Others 5% each")
    preferences = {
        'offensive_weight': 0.50,
        'defensive_weight': 0.05,
        'longevity_weight': 0.05,
        'team_success_weight': 0.30,
        'efficiency_weight': 0.05,
        'peak_performance_weight': 0.05
    }

    total_weight = sum(preferences.values())
    print(f"  Total weight: {total_weight}")

    normalized = {k: v / total_weight for k, v in preferences.items()}
    print(f"  Normalized weights sum: {sum(normalized.values())}")
    for k, v in normalized.items():
        print(f"    {k}: {v:.3f} ({v*100:.1f}%)")

    # Test Case 3: Only one category (should be 100%)
    print("\nTest Case 3: Only Peak Performance matters (100%)")
    preferences = {
        'offensive_weight': 0.0,
        'defensive_weight': 0.0,
        'longevity_weight': 0.0,
        'team_success_weight': 0.0,
        'efficiency_weight': 0.0,
        'peak_performance_weight': 1.0
    }

    total_weight = sum(preferences.values())
    print(f"  Total weight: {total_weight}")

    if total_weight == 0:
        total_weight = 1.0  # Prevent division by zero

    normalized = {k: v / total_weight for k, v in preferences.items()}
    print(f"  Normalized weights sum: {sum(normalized.values())}")
    for k, v in normalized.items():
        print(f"    {k}: {v:.3f} ({v*100:.1f}%)")

    # Test Case 4: Verify final score calculation
    print("\nTest Case 4: Score calculation with equal category scores")
    preferences = {
        'offensive_weight': 0.40,  # 40%
        'defensive_weight': 0.20,  # 20%
        'longevity_weight': 0.10,  # 10%
        'team_success_weight': 0.10,  # 10%
        'efficiency_weight': 0.10,   # 10%
        'peak_performance_weight': 0.10  # 10%
    }

    # Simulate category scores (all 80/100)
    category_scores = {
        'offensive': 80,
        'defensive': 80,
        'longevity': 80,
        'team_success': 80,
        'efficiency': 80,
        'peak_performance': 80
    }

    total_weight = sum(preferences.values())
    normalized = {k: v / total_weight for k, v in preferences.items()}

    total_score = (
        category_scores['offensive'] * normalized['offensive_weight'] +
        category_scores['defensive'] * normalized['defensive_weight'] +
        category_scores['longevity'] * normalized['longevity_weight'] +
        category_scores['team_success'] * normalized['team_success_weight'] +
        category_scores['efficiency'] * normalized['efficiency_weight'] +
        category_scores['peak_performance'] * normalized['peak_performance_weight']
    )

    print(f"  All category scores: 80/100")
    print(f"  Total weight: {total_weight}")
    print(f"  Normalized weights sum: {sum(normalized.values())}")
    print(f"  Final score: {total_score:.2f}/100")
    print(f"  Expected: 80.00 (since all categories are equal)")

    # Test Case 5: Different category scores with different weights
    print("\nTest Case 5: Different scores, different weights")
    preferences = {
        'offensive_weight': 0.50,  # 50%
        'defensive_weight': 0.10,  # 10%
        'longevity_weight': 0.10,  # 10%
        'team_success_weight': 0.10,  # 10%
        'efficiency_weight': 0.10,  # 10%
        'peak_performance_weight': 0.10  # 10%
    }

    category_scores = {
        'offensive': 95,      # High offensive score
        'defensive': 50,      # Low defensive
        'longevity': 60,
        'team_success': 70,
        'efficiency': 80,
        'peak_performance': 90
    }

    total_weight = sum(preferences.values())
    normalized = {k: v / total_weight for k, v in preferences.items()}

    total_score = (
        category_scores['offensive'] * normalized['offensive_weight'] +
        category_scores['defensive'] * normalized['defensive_weight'] +
        category_scores['longevity'] * normalized['longevity_weight'] +
        category_scores['team_success'] * normalized['team_success_weight'] +
        category_scores['efficiency'] * normalized['efficiency_weight'] +
        category_scores['peak_performance'] * normalized['peak_performance_weight']
    )

    print(f"  Category scores:")
    for k, v in category_scores.items():
        weight_key = k + '_weight'
        print(f"    {k}: {v}/100 (weight: {normalized[weight_key]:.3f})")
    print(f"  Total weight: {total_weight}")
    print(f"  Normalized weights sum: {sum(normalized.values())}")
    print(f"  Final score: {total_score:.2f}/100")
    print(f"  Manual calculation: 95*0.5 + 50*0.1 + 60*0.1 + 70*0.1 + 80*0.1 + 90*0.1 = {95*0.5 + 50*0.1 + 60*0.1 + 70*0.1 + 80*0.1 + 90*0.1:.2f}")

if __name__ == '__main__':
    test_weight_normalization()
