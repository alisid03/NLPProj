# ✈️ FlightAI – Smart Flight Booking Chatbot

**FlightAI** is a voice- and text-enabled AI-powered chatbot built with OpenAI’s GPT and Gradio. It allows users to search flights, check prices and availability, and make bookings in natural language. Bookings come with downloadable PDF receipts, and speech interaction is supported for hands-free use.

---

## 🚀 Features

- 💬 Conversational interface using OpenAI's GPT-4o-mini
- 🗣️ Voice input and text-to-speech using Vosk + gTTS
- 📅 Real-time flight search from a PostgreSQL (Supabase) database
- 📄 Generates downloadable booking receipts in PDF
- 📦 Gradio UI for seamless interaction
- 🧠 Modular tool-calling backend architecture

---

## 🛠️ Tech Stack

- **Language:** Python 3.10+
- **Frontend:** Gradio
- **Backend:** PostgreSQL (via Supabase), OpenAI GPT-4o-mini
- **Speech Recognition:** Vosk
- **Text-to-Speech:** gTTS + Pygame
- **PDF Generation:** FPDF

---

## 📁 Folder Structure

```
.
├── data/                # (Optional) Local SQLite flight/booking database
├── receipts/            # Stores generated PDF booking receipts
├── src/
│   ├── main.py          # Main Gradio app entry point
│   ├── chatbot.py       # Chat handling and GPT interaction
│   ├── db.py            # PostgreSQL/Supabase connection and queries
│   ├── airport.py       # Airport and city mapping
│   ├── functions.py     # Flight logic: booking, search, price
│   ├── resendEmail.py   # (Optional) Email receipt logic
│   ├── tools.py         # OpenAI-compatible tool definitions
│   └── speech.py        # Speech-to-text and TTS logic
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

---

## 🧪 Running Locally

### Prerequisites

- Python ≥ 3.10
- An OpenAI API key
- PostgreSQL database (or Supabase)
- PortAudio (required by PyAudio)

### Installation

```bash
git clone https://github.com/alisid03/NLPProj.git
cd NLPProj
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` file in the root directory and add the following:

```env
# OpenAI API Key
OPENAI_API_KEY=your-openai-key-here

# Supabase/PostgreSQL Database Config
DB_NAME=postgres
DB_USER=postgres.dqwpvibaabcqigdoujhc
DB_PASSWORD=FlightAI-2025!
DB_HOST=aws-0-us-east-1.pooler.supabase.com
DB_PORT=6543
```

> These variables are loaded using `python-dotenv` to securely configure the chatbot and database access.

---

## 🎙️ Speech Recognition Setup

To enable speech-to-text functionality using [Vosk](https://alphacephei.com/vosk/), download the English model:

### Step 1: Download the Vosk Model

You can download the small English model (recommended for faster loading) from the official site:

```
https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
```

Or use the command line:

```bash
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
mv vosk-model-small-en-us-0.15 model
```

> This will place the model into a folder called `model/`. Make sure your code points to this directory in `speech.py`.

### Step 2: Confirm Your `speech.py` Uses the Model

In `speech.py`, ensure the model is loaded with:

```python
model = vosk.Model("model")
```

---

## ▶️ Launch the App

```bash
python app.py
```

Gradio will start a local web server where you can interact with FlightAI.

---

## 💬 Sample Prompts

- "Find me a flight from Dallas to New York on June 12th."
- "What’s the cheapest flight from Seattle to Boston?"
- "Book a flight to Chicago under the name Alex."
- "Show bookings for Sarah Smith."

---


---

## 🧩 Tool Functions

FlightAI uses OpenAI function calling with a set of modular tools defined in `tools.py` and implemented in `functions.py`. Here’s the full list:

### ✈️ Flight Tools

- **get_flights_exact**  
  Find flights between two specific cities.  
  Parameters: `departure_city`, `destination_city`

- **get_flights_from_surrounding_city**  
  Suggests flights from surrounding cities near the departure city.  
  Parameters: `departure_city`, `destination_city`

- **get_flights_by_date**  
  Retrieves flights between two cities on a specific date.  
  Parameters: `departure_city`, `destination_city`, `date`

- **get_flight_by_airline**  
  Lists all flights for a given airline.  
  Parameters: `airline_name`

- **get_flight_status**  
  Returns the status of a flight based on flight number.  
  Parameters: `flight_number`

### 💳 Booking & Pricing Tools

- **get_ticket_price**  
  Fetches the ticket price for a given destination.  
  Parameters: `destination_city`

- **get_available_seats**  
  Checks seat availability for a flight to a city.  
  Parameters: `destination_city`

- **book_ticket**  
  Books a ticket for a user.  
  Parameters: `user_name`, `flight_number`

- **cancel_booking**  
  Cancels an existing booking.  
  Parameters: `booking_id`

### 👤 User Tools

- **get_user_bookings**  
  Retrieves bookings associated with a user's name.  
  Parameters: `user_name`

- **create_account**  
  Creates a user account with name, email, and phone.  
  Parameters: `name`, `email`, `phone`

### 🛫 Airport Tools

- **get_airport_code**  
  Returns the airport code for a given city.  
  Parameters: `city`

- **get_nearby_airports**  
  Lists nearby airports based on the input city.  
  Parameters: `city`


