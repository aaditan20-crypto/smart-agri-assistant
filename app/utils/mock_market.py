import random

def get_mock_market_data(crop_name: str, location: str) -> dict:
    """
    Simulates current market price and a short price trend for a crop.
    Replace this later with a real API call (e.g. Agmarknet / data.gov.in)
    without changing anything else in the pipeline.
    """
    base_price = round(random.uniform(1500, 6000), 2)  # per quintal, in INR

    trend = []
    price = base_price
    for week in range(1, 5):
        change_percent = random.uniform(-8, 8)
        price = round(price * (1 + change_percent / 100), 2)
        trend.append({"week": week, "price_per_quintal": price})

    nearby_markets = [
        f"{location} APMC Market",
        f"{location} District Mandi",
        "Regional Wholesale Market"
    ]

    return {
        "crop_name": crop_name,
        "current_price_per_quintal": base_price,
        "price_trend_next_4_weeks": trend,
        "nearby_markets": nearby_markets
    }