import torch
import torch.nn as nn

class FraudRiskModel(nn.Module):
    def __init__(self, input_size=4):
        super(FraudRiskModel, self).__init__()
        
        # Layer 1: Takes the 4 features and expands them to 16 hidden nodes
        self.layer1 = nn.Linear(input_size, 16)
        self.relu1 = nn.ReLU() # Activation function to learn complex patterns
        
        # Dropout: Randomly turns off 20% of nodes during training to prevent overfitting
        self.dropout = nn.Dropout(0.2)
        
        # Layer 2: Compresses 16 nodes down to 8
        self.layer2 = nn.Linear(16, 8)
        self.relu2 = nn.ReLU()
        
        # Output Layer: Compresses 8 nodes into 1 final prediction
        self.output_layer = nn.Linear(8, 1)
        self.sigmoid = nn.Sigmoid() # Squashes output between 0 and 1 (Probability)

    def forward(self, x):
        # This defines the forward pass (how data flows through the network)
        x = self.layer1(x)
        x = self.relu1(x)
        x = self.dropout(x)
        
        x = self.layer2(x)
        x = self.relu2(x)
        
        x = self.output_layer(x)
        x = self.sigmoid(x)
        return x

# Quick test to make sure the architecture works
if __name__ == "__main__":
    # Create a dummy tensor representing 1 row of our 4 features
    dummy_input = torch.randn(1, 4) 
    
    # Initialize the model
    model = FraudRiskModel()
    
    # Pass the dummy data through the model
    prediction = model(dummy_input)
    
    print(f"Model successfully built!")
    print(f"Input shape: {dummy_input.shape}")
    print(f"Output prediction (Risk Score): {prediction.item():.4f}")