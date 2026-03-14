import os
from twilio.rest import Client

# 1. Get these from the main Twilio Console Dashboard
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# 2. Make the Outbound Call
call = client.calls.create(
    to='+91 72178 43077', # The Indian number you just verified
    from_='+1 856 636 3795', # Your Twilio Trial Number
    
    # 3. THIS IS THE BRIDGE! 
    # We tell Twilio: "When the user answers, get instructions from the Ngrok server!"
    url='https://geniculate-unentangled-merna.ngrok-free.dev/twiml', 
    
    status_callback='https://geniculate-unentangled-merna.ngrok-free.dev/call_status',
    status_callback_event=['completed']
)

print(f"Calling your phone right now! Call SID: {call.sid}")