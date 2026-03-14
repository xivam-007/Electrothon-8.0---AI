import pandas as pd
import numpy as np
import random

def generate_synthetic_data(num_samples=500):
    np.random.seed(42)
    
    # Generate base features
    distances = np.random.randint(10, 2500, num_samples) # in km
    inventory_sizes = np.random.randint(1, 5, num_samples) # 1 to 4 BHK
    mover_ratings = np.round(np.random.uniform(1.0, 5.0, num_samples), 1)
    
    # Calculate a "fair" base price
    base_prices = (distances * 30) + (inventory_sizes * 5000)
    
    # Generate initial quotes (some normal, some suspiciously low to bait users)
    initial_quotes = []
    hidden_cost_flags = []
    
    for i in range(num_samples):
        rating = mover_ratings[i]
        fair_price = base_prices[i]
        
        # Fraud logic: Low rating + suspiciously low quote (bait and switch) = high hidden cost probability
        if rating < 3.0 and random.random() > 0.3:
            quote = fair_price * np.random.uniform(0.5, 0.7) # 30-50% cheaper than it should be
            hidden_cost_flags.append(1)
        else:
            quote = fair_price * np.random.uniform(0.9, 1.2) # Normal pricing
            # Add some random noise for real-world variance
            hidden_cost_flags.append(1 if random.random() > 0.85 else 0)
            
        initial_quotes.append(int(quote))

    # Create DataFrame
    df = pd.DataFrame({
        'distance_km': distances,
        'inventory_size': inventory_sizes,
        'mover_rating': mover_ratings,
        'initial_quote': initial_quotes,
        'hidden_cost_flag': hidden_cost_flags
    })
    
    df.to_csv('mock_moving_data.csv', index=False)
    print(f"Generated {num_samples} rows in 'mock_moving_data.csv'")

if __name__ == "__main__":
    generate_synthetic_data()