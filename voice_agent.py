import os
import json
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# Import your HYBRID PyTorch model!
from predict import get_fraud_risk_score 

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 1. GLOBAL MEMORY ---
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
chat_history = []
current_move_data = {} 

# --- 2. DB DATA STRUCTURE (What Node.js sends us) ---
class MoveRequest(BaseModel):
    move_id: str
    pickup_location: str
    drop_location: str
    weight: str
    target_price: float # This is the calculated formula price!
    distance_km: str
    pickup_date: str = "soon"
    pickup_time: str = "morning"
    # 👇 NEW: We need Node.js to send the mover's stats for the Risk Engine
    rating: float
    total_reviews: int 

# --- 3. THE TRIGGER ---
@app.post("/trigger_negotiation")
async def trigger_negotiation(move_details: MoveRequest):
    print(f"\n🚀 Waking up! Received Move from Node.js: {move_details.pickup_location} to {move_details.drop_location}")
    
    # Save the DB data to global memory so we can use it when the call ends!
    current_move_data['move_id'] = move_details.move_id
    current_move_data['distance_km'] = move_details.distance_km
    current_move_data['calculated_price'] = move_details.target_price
    current_move_data['rating'] = move_details.rating
    current_move_data['total_reviews'] = move_details.total_reviews
    
    # Base prompt
    dynamic_prompt = f"""
    ROLE AND CONTEXT:
    You are Makkhan Move's AI Dispatch Manager. You are calling a truck driver (vendor) to hire them for a shifting job. 
    You already have the customer's booking details. Your only job is to check if the driver is available and negotiate the price.

    THE JOB DETAILS (YOU ALREADY KNOW THESE - DO NOT ASK THE DRIVER FOR THEM):
    - Pickup Location: {move_details.pickup_location}
    - Drop Location: {move_details.drop_location}
    - Goods/Weight: {move_details.weight}
    - Required Date: {move_details.pickup_date}
    - Required Time: {move_details.pickup_time}

    YOUR GOAL & NEGOTIATION STRATEGY:
    1. Tell the driver the locations, date, and time, and ask if their truck is available.
    2. Your target budget is ₹{move_details.target_price}. 
    3. If the driver quotes a price higher than ₹{move_details.target_price + 2000}, firmly negotiate. Say your budget is strict and ask them to lower it.
    4. If the driver quotes a price equal to or lower than ₹{move_details.target_price}, immediately agree and lock the deal.

    STRICT RULES:
    1. HINGLISH ONLY: Speak in a natural mix of Hindi and English. (e.g., "Bhaiya ek shifting hai, aap available ho?")
    2. NEVER ASK THE DRIVER FOR THE DATE/TIME: You tell them the date and time ({move_details.pickup_date} at {move_details.pickup_time}) and ask if they can do it.
    3. KEEP IT BRIEF: You are on a phone call. Maximum 1 or 2 short sentences per response. 
    4. FINAL CONFIRMATION: Before ending the call, you MUST summarize and confirm the final agreed price, the pickup date, and the pickup time.
    """
    
    
    
    chat_history.clear()
    chat_history.append(SystemMessage(content=dynamic_prompt))
    
    client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
    MY_PYTHON_NGROK_URL = "https://geniculate-unentangled-merna.ngrok-free.dev" # Replace with your ngrok
    
    try:
        call = client.calls.create(
            to='+917217843077', 
            from_='+18566363795',
            url=f'{MY_PYTHON_NGROK_URL}/twiml',
            status_callback=f'{MY_PYTHON_NGROK_URL}/call_status',
            status_callback_event=['completed']
        )
        print(f"📞 Twilio is dialing now... Call SID: {call.sid}")
        return {"status": "success", "message": "Phone is ringing!"}
    except Exception as e:
        print(f"❌ Twilio Error: {e}")
        return {"status": "error", "message": str(e)}

# --- 4. THE CONVERSATION LOOP ---
@app.post("/twiml")
async def get_twiml(request: Request):
    response = VoiceResponse()
    greeting = f"Namaste! Main Makkhan Move se call kar rahi hoon. Ek shifting requirement discuss karni thi aapse."
    chat_history.append(AIMessage(content=greeting))
    
    gather = Gather(input="speech", action="/process_speech", language="hi-IN", speechTimeout="auto")
    gather.say(greeting, voice="Google.en-IN-Wavenet-E")
    response.append(gather)
    return HTMLResponse(content=str(response), media_type="application/xml")

@app.post("/process_speech")
async def process_speech(SpeechResult: str = Form(None)):
    response = VoiceResponse()
    if not SpeechResult:
        gather = Gather(input="speech", action="/process_speech", language="hi-IN", speechTimeout="auto")
        gather.say("Hello? Aap sun pa rahe hain?", voice="Google.en-IN-Wavenet-E")
        response.append(gather)
        return HTMLResponse(content=str(response), media_type="application/xml")

    print(f"👤 Driver said: {SpeechResult}")
    chat_history.append(HumanMessage(content=SpeechResult))
    
    ai_reply = llm.invoke(chat_history).content
    print(f"🤖 AI replying: {ai_reply}")
    chat_history.append(AIMessage(content=ai_reply))
    
    gather = Gather(input="speech", action="/process_speech", language="hi-IN", speechTimeout="auto")
    gather.say(ai_reply, voice="Google.en-IN-Wavenet-E")
    response.append(gather)
    return HTMLResponse(content=str(response), media_type="application/xml")

# --- 5. THE DATA MERGE & BOOMERANG ---
@app.post("/call_status")
async def call_status(CallStatus: str = Form(None)):
    if CallStatus in ["completed", "failed", "busy", "no-answer"]:
        print("\n" + "="*50)
        print("🛑 Call Ended. Extracting dynamic data from the AI conversation...")
        
        # 👇 NEW: Extracting the Time and Date the AI negotiated!
        extraction_prompt = f"""
        Read this chat history and extract the final agreed terms.
        Output ONLY a valid JSON object with these exact keys:
        - final_price: (integer) The final agreed amount in INR. Put 0 if no agreement.
        - pickup_date: (string) The agreed date (YYYY-MM-DD). Leave empty if not discussed.
        - pickup_time: (string) The agreed time (e.g., "14:00" or "2 PM"). Leave empty if not discussed.
        Chat History: {chat_history}
        """
        
        try:
            extraction_result = llm.invoke([SystemMessage(content=extraction_prompt)]).content
            clean_json = extraction_result.replace("```json", "").replace("```", "").strip()
            final_deal = json.loads(clean_json)
            print(f"✅ AI Extracted: {final_deal}")
            
            # --- MERGING DB DATA WITH AI DATA ---
            # 1. Static Data from Node.js Database
            # distance = float(current_move_data.get('distance_km', 100))
            # inventory = 2 # Fixed for now
            rating = current_move_data.get('rating', 4.0)
            total_reviews = current_move_data.get('total_reviews', 50)
            calculated_price = current_move_data.get('calculated_price', 15000)
            
            # 2. Dynamic Data from the Phone Call
            negotiated_price = final_deal.get("final_price", 0)
            negotiated_date = final_deal.get("pickup_date", "")
            negotiated_time = final_deal.get("pickup_time", "")
            
            if negotiated_price > 0:
                print(f"🧠 Running Hybrid Risk Engine...")
                
                # RUN THE NEW FUNCTION WE JUST BUILT
                risk_score = get_fraud_risk_score( 
                    rating=rating, 
                    quoted_price=negotiated_price, 
                    calculated_price=calculated_price, 
                    total_reviews=total_reviews
                )
                
                is_safe = bool(risk_score < 70.0)
                print(f"🚨 Final Risk Score: {risk_score:.2f}% | Safe: {is_safe}")
                
                # --- SHOOT IT ALL BACK TO NODE.JS ---
                NODE_WEBHOOK_URL = "http://localhost:8000/update-from-ai" # Update to teammate's ngrok
                
                payload = {
                    "moveId": current_move_data.get('move_id'),
                    "finalPrice": negotiated_price,
                    "deliveryDate": negotiated_date, # Sending negotiated date back!
                    "deliveryTime": negotiated_time, # Sending negotiated time back!
                    "riskScore": round(risk_score, 2),
                    "isSafe": is_safe,
                    "moverId": "asdfas"
                }
                
                requests.post(NODE_WEBHOOK_URL, json=payload)
                print("✅ Webhook fired to Node.js backend!")
            else:
                print("⚠️ No final price agreed. Skipping update.")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            
        print("="*50 + "\n")

    return HTMLResponse(content="", status_code=200)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("voice_agent:app", host="0.0.0.0", port=8000, reload=True)