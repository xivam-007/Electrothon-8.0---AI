def get_fraud_risk_score(calculated_price, quoted_price, rating, total_reviews):
    """
    Calculates Fraud Risk based strictly on:
    1. Price Difference (Hostage Scam Check)
    2. Google Rating
    3. Total Number of Reviews (Ghost Company Check)
    """
    risk_score = 0.0

    print(f"🔍 Analyzing Driver -> Quoted: ₹{quoted_price} | Formula: ₹{calculated_price} | Rating: {rating} | Reviews: {total_reviews}")

    # --- FACTOR 1: Price Difference ---
    # Are they quoting a price that is suspiciously "Too Good To Be True"?
    price_diff = calculated_price - quoted_price
    percentage_diff = (price_diff / calculated_price) * 100

    if percentage_diff > 30:
        # Massive Red Flag: Quoting 30% cheaper than the real-world math. 
        # Classic hostage scam setup (they will demand more money mid-trip).
        risk_score += 50.0
        print(f"   🚩 PENALTY: Price is suspiciously low ({percentage_diff:.1f}% under formula)")
    elif percentage_diff > 15:
        risk_score += 25.0
        print(f"   ⚠️ PENALTY: Price is notably low ({percentage_diff:.1f}% under formula)")
    elif percentage_diff < -20:
        # Quoting 20% higher than formula. Not a hostage scam, but a rip-off.
        risk_score += 15.0
        print(f"   ⚠️ PENALTY: Price is heavily overpriced")

    # --- FACTOR 2: Rating ---
    if rating < 3.0:
        risk_score += 30.0
        print(f"   🚩 PENALTY: Terrible review average ({rating} stars)")
    elif rating < 4.0:
        risk_score += 10.0
        print(f"   ⚠️ PENALTY: Mediocre review average ({rating} stars)")

    # --- FACTOR 3: Total Reviews ---
    # A 5-star rating means nothing if only 2 people reviewed it (fake burner accounts).
    if total_reviews < 10:
        risk_score += 20.0
        print(f"   🚩 PENALTY: Dangerously low review count ({total_reviews} total)")
    elif total_reviews < 50:
        risk_score += 10.0
        print(f"   ⚠️ PENALTY: Low review count ({total_reviews} total)")

    # Ensure the score mathematically stays between 0% and 100%
    final_risk = min(risk_score, 100.0)
    
    return final_risk

if __name__ == "__main__":
    print("Testing Makhan Move Math Engine...\n")
    
    # Test Case 1: Safe Mover (Good price, good rating, lots of reviews)
    safe_score = get_fraud_risk_score(
        calculated_price=50000, 
        quoted_price=48000, 
        rating=4.5, 
        total_reviews=200
    )
    print(f"🏆 Test 1 (Safe) -> Final Risk: {safe_score:.2f}%\n")
    
    # Test Case 2: Hostage Scam Bait (Way too cheap, bad rating, fake reviews)
    scam_score = get_fraud_risk_score(
        calculated_price=50000, 
        quoted_price=20000, 
        rating=2.1, 
        total_reviews=4
    )
    print(f"🚨 Test 2 (Scam) -> Final Risk: {scam_score:.2f}%\n")