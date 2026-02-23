from database import get_fill_history
from datetime import datetime

def predict_overflow(bin_id):
    """
    Looks at fill history of a bin and predicts
    how many hours until it overflows (reaches 100%)
    """
    history = get_fill_history(bin_id)

    if len(history) < 2:
        return {
            "bin_id": bin_id,
            "prediction": "Not enough data",
            "hours_to_overflow": None,
            "urgency": "UNKNOWN"
        }

    # Get fill levels in order (oldest first)
    levels = [(row[0], row[1]) for row in reversed(history)]

    # Calculate average fill rate per hour
    fill_rates = []
    for i in range(1, len(levels)):
        level_diff = levels[i][0] - levels[i-1][0]

        time1 = datetime.strptime(levels[i-1][1], "%Y-%m-%d %H:%M:%S")
        time2 = datetime.strptime(levels[i][1], "%Y-%m-%d %H:%M:%S")
        time_diff = (time2 - time1).total_seconds() / 3600  # in hours

        if time_diff > 0:
            rate = level_diff / time_diff
            fill_rates.append(rate)

    if not fill_rates:
        return {
            "bin_id": bin_id,
            "prediction": "Cannot calculate",
            "hours_to_overflow": None,
            "urgency": "UNKNOWN"
        }

    avg_rate = sum(fill_rates) / len(fill_rates)
    current_fill = levels[-1][0]
    remaining = 100 - current_fill

    if avg_rate <= 0:
        return {
            "bin_id": bin_id,
            "prediction": "Fill rate stable or decreasing",
            "hours_to_overflow": None,
            "urgency": "LOW"
        }

    hours_to_overflow = remaining / avg_rate

    # Determine urgency
    if hours_to_overflow <= 2:
        urgency = "CRITICAL"
        message = f"Will overflow in {round(hours_to_overflow, 1)} hours — collect IMMEDIATELY"
    elif hours_to_overflow <= 6:
        urgency = "HIGH"
        message = f"Will overflow in {round(hours_to_overflow, 1)} hours — schedule today"
    elif hours_to_overflow <= 24:
        urgency = "MEDIUM"
        message = f"Will overflow in {round(hours_to_overflow, 1)} hours — schedule tomorrow"
    else:
        urgency = "LOW"
        message = f"Will overflow in {round(hours_to_overflow, 1)} hours — no rush"

    return {
        "bin_id": bin_id,
        "current_fill": current_fill,
        "fill_rate_per_hour": round(avg_rate, 2),
        "hours_to_overflow": round(hours_to_overflow, 1),
        "urgency": urgency,
        "prediction": message
    }


def predict_all_bins(bin_ids):
    """
    Predict overflow for all bins at once
    Returns sorted by urgency (most critical first)
    """
    results = []
    for bin_id in bin_ids:
        result = predict_overflow(bin_id)
        results.append(result)

    # Sort by hours to overflow (critical first)
    results.sort(key=lambda x: x.get("hours_to_overflow") or 9999)

    return results