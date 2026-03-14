import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from dataset_loader import MoverDataset
from model import FraudRiskModel

# 1. Hardware Setup (Use your M2 chip!)
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
print(f"Training on device: {device}")

# 2. Load the Data
dataset = MoverDataset('mock_moving_data.csv')
dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

# 3. Initialize the Model
model = FraudRiskModel().to(device)

# 4. Define the "Teacher" (Loss Function) and the "Learner" (Optimizer)
# BCELoss = Binary Cross Entropy. It's the standard math for Yes/No (Scam/Safe) guessing.
criterion = nn.BCELoss() 
# Adam is the standard, highly efficient optimizer that adjusts the brain's weights.
optimizer = optim.Adam(model.parameters(), lr=0.001) 

# 5. The Training Loop (Sending it to school for 50 "Epochs" or semesters)
epochs = 50

print("Starting training...")
for epoch in range(epochs):
    epoch_loss = 0.0
    
    for features, labels in dataloader:
        # Move data to your M2 GPU
        features, labels = features.to(device), labels.to(device)
        
        # Step A: Clear old memories (gradients)
        optimizer.zero_grad()
        
        # Step B: Forward Pass (Make a guess)
        predictions = model(features)
        
        # Step C: Calculate the Error (How wrong was the guess?)
        loss = criterion(predictions, labels)
        
        # Step D: Backward Pass (Learn from the mistake - the "Backpropagation")
        loss.backward()
        
        # Step E: Update the brain's weights
        optimizer.step()
        
        epoch_loss += loss.item()
        
    # Print progress every 10 epochs
    if (epoch + 1) % 10 == 0:
        avg_loss = epoch_loss / len(dataloader)
        print(f"Epoch [{epoch+1}/{epochs}], Loss (Error Rate): {avg_loss:.4f}")

# 6. Save the trained brain to a file!
torch.save(model.state_dict(), 'makhan_fraud_model.pth')
print("Training complete! Model saved as 'makhan_fraud_model.pth'")