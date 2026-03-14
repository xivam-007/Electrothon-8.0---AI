import torch
from torch.utils.data import Dataset, DataLoader
import pandas as pd
from sklearn.preprocessing import StandardScaler

# Hardware acceleration check
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
print(f"Using device: {device}")

class MoverDataset(Dataset):
    def __init__(self, csv_file):
        df = pd.read_csv(csv_file)
        
        # Separate features (X) and target (y)
        self.X = df[['distance_km', 'inventory_size', 'mover_rating', 'initial_quote']].values
        self.y = df['hidden_cost_flag'].values
        
        # Normalize the features so the neural net learns effectively
        self.scaler = StandardScaler()
        self.X = self.scaler.fit_transform(self.X)
        
        # Convert to PyTorch tensors
        self.X = torch.tensor(self.X, dtype=torch.float32)
        self.y = torch.tensor(self.y, dtype=torch.float32).unsqueeze(1)

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

if __name__ == "__main__":
    # Test the dataloader
    dataset = MoverDataset('mock_moving_data.csv')
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
    
    # Grab one batch to verify
    features, labels = next(iter(dataloader))
    print(f"Features batch shape: {features.shape}")
    print(f"Labels batch shape: {labels.shape}")