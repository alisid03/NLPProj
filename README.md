title: FlightAI
emoji: 💬
colorFrom: yellow
colorTo: purple
sdk: gradio
sdk_version: 5.0.1
app_file: app.py
pinned: false
short_description: A flight ai chatbot

# ✈️ Flight Booking Chatbot

A conversational Python chatbot that helps users search and book flights. It integrates OpenAI's GPT model for intelligent query parsing and uses SQLite to store flight and booking data.

---

## 🧠 Features

- Natural language understanding powered by GPT (via OpenAI API)
- Flight search with flexible date ranges and route parsing
- SQLite database for storing flights and user bookings
- Interactive CLI chatbot interface
- View existing bookings by name and address
- Easy flight selection and booking confirmation

---

## 🚀 Getting Started

### 🔧 Prerequisites

- Python 3.7+
- An OpenAI API key (`https://platform.openai.com`)
- SQLite3

### 📦 Installation

1. **Clone the repo**
```bash
git clone https://github.com/your-username/flight-booking-chatbot.git
cd flight-booking-chatbot
```

2. **Install dependencies**
```bash
pip install openai
```

3. **Initialize the database**
```python
# This is done automatically when the script runs
# But you can call the method manually if needed
create_and_populate_flights_table()
```

## 💬 How to Use

1. Run the chatbot:
```bash
python chatbot.py
```

2. Interact via command-line:

```text
Chatbot: Welcome to the airflight booking chatbot.
You: I want to fly from Dallas to New York on April 20th.
Chatbot: [returns matching flights]
You: book
Chatbot: Please enter your name
You: Ajwad Masood
Chatbot: Please enter your address
You: 123 Maple Lane
```

3. To view existing bookings:
```text
You: view bookings
```

4. To exit:
```text
You: exit
```

## 🧱 Built With

- [Python](https://www.python.org/)
- [OpenAI GPT](https://platform.openai.com/)
- [SQLite3](https://sqlite.org/)
- Standard libraries: `json`, `sqlite3`, `input/output`
