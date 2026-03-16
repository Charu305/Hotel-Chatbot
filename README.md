# 🏨 Hotel Chatbot — NLP-Powered Conversational Assistant

> **An NLP-based conversational chatbot** for hotel guest interactions — capable of understanding natural language queries, recognising user intent, retrieving food menu information, and responding intelligently to hotel-related requests like room bookings, dining, and service enquiries.

---

## 📌 Project Overview

Hotels receive hundreds of repetitive guest queries daily — room availability, food orders, check-in times, amenity information. A conversational chatbot can handle these 24/7 without human intervention, improving guest experience while reducing front desk load.

This project builds a **domain-specific hotel assistant chatbot** that:
- Understands free-form natural language input from guests
- Classifies the **intent** behind each message (e.g., menu query, booking, complaint)
- Retrieves relevant responses from structured data (`FoodMenu.json`)
- Maintains a coherent, context-aware conversation flow
- Is powered by a modular Python utility layer (`utils.py`) separating logic from the notebook

---

## 🎯 Problem Statement

> *Build a conversational AI agent that can understand hotel guest queries in natural language and respond accurately — covering food orders, room services, bookings, and general hotel information.*

**Real-world applications:**
- Hotel website / app live chat assistant
- WhatsApp or messaging platform bot for guest services
- In-room tablet assistant for service requests
- Front desk overflow support during peak hours

---

## 🏗️ System Architecture

```
Guest Input (Natural Language)
            │
            ▼
┌──────────────────────────────┐
│   Text Preprocessing         │
│   Tokenization, lowercasing  │
│   Stopword removal           │
└────────────┬─────────────────┘
             │
             ▼
┌──────────────────────────────┐
│   Intent Recognition         │
│   Classifies user message    │
│   into predefined intents:   │
│   menu / booking / greeting  │
│   complaint / checkout etc.  │
└────────────┬─────────────────┘
             │  Identified intent
             ▼
┌──────────────────────────────┐
│   Response Generation        │
│   Rule-based / retrieval     │
│   FoodMenu.json lookup       │
│   utils.py helper functions  │
└────────────┬─────────────────┘
             │
             ▼
      Chatbot Response to Guest
```

---

## 🗂️ Project Structure

```
Hotel-Chatbot/
│
├── Hotel-Chatbot.ipynb    # Main chatbot pipeline — training, intent classification & conversation loop
├── utils.py               # Reusable utility functions — preprocessing, response helpers, menu lookup
├── FoodMenu.json          # Structured hotel food menu data (items, prices, categories)
└── README.md
```

---

## 🔬 Technical Deep Dive

### 1. Intent Definition & Training Data

The chatbot is built around a set of **predefined intents** — each representing a category of guest query:

| Intent | Example Guest Messages |
|---|---|
| `greeting` | "Hello", "Hi there", "Good morning" |
| `menu_query` | "What's on the menu?", "Do you have pasta?" |
| `food_order` | "I'd like to order a pizza", "Can I get breakfast to my room?" |
| `room_service` | "Can I get extra towels?", "Please clean my room" |
| `booking` | "I want to book a room", "Do you have availability?" |
| `checkout` | "What time is checkout?", "I want to check out now" |
| `complaint` | "The AC isn't working", "My room is too noisy" |
| `farewell` | "Goodbye", "Thank you, bye" |

Each intent has multiple **training utterances** (different ways a guest might express the same need) — this variety is critical for the model to generalise beyond exact phrase matches.

### 2. Text Preprocessing (`utils.py`)

The `utils.py` module contains reusable preprocessing and helper functions:
- **Tokenization** — splits guest input into individual words/tokens
- **Lowercasing** — normalises text so "Menu" and "menu" are treated identically
- **Stopword removal** — removes filler words that don't carry intent signal
- **Stemming / Lemmatization** — reduces words to root form for better generalisation
- **Menu lookup functions** — queries `FoodMenu.json` for item availability, pricing, and descriptions

Separating these into `utils.py` rather than embedding them in the notebook reflects good software engineering practice — reusable, testable, and importable.

### 3. Intent Classification Model

- Converted preprocessed training utterances into **numerical feature vectors** using:
  - **Bag-of-Words (CountVectorizer)** or **TF-IDF** — for classical ML classifiers
  - **Word Embeddings** — for neural approaches
- Trained a classifier to map input vectors to intent labels:
  - Logistic Regression / SVM — fast, interpretable baseline
  - Neural Network / LSTM — better generalisation on varied phrasing
- Evaluated classification accuracy on a held-out validation set of unseen utterances.

### 4. Menu Integration (`FoodMenu.json`)

- `FoodMenu.json` stores the hotel's food menu in a structured format — categories, item names, descriptions, and prices.
- When a `menu_query` or `food_order` intent is detected, the bot dynamically queries this JSON to return accurate, up-to-date menu information.
- This design decouples the **menu data** from the **model** — updating the menu requires only editing the JSON, not retraining the model.

### 5. Response Generation

- **Template-based responses** for intents with fixed answers (greetings, checkout times, farewell)
- **Dynamic retrieval responses** for data-dependent intents (menu queries, room availability)
- **Fallback response** when intent confidence is below threshold — e.g., "I didn't quite understand that. Could you rephrase?"

### 6. Conversation Loop

- The notebook implements an interactive **conversation loop** that:
  - Accepts guest input
  - Preprocesses and classifies intent
  - Selects and returns the appropriate response
  - Continues until the guest signals farewell

---

## 📊 Model Performance

| Metric | Description |
|---|---|
| **Intent Accuracy** | Percentage of guest inputs mapped to the correct intent |
| **Confidence Threshold** | Minimum probability required before returning a response vs. fallback |
| **Coverage** | Percentage of test queries handled without triggering the fallback |

---

## 🛠️ Tech Stack

| Category | Tools |
|---|---|
| Language | Python 3 |
| NLP Preprocessing | NLTK, RegEx |
| Feature Extraction | Scikit-learn (TF-IDF / CountVectorizer) |
| Intent Classification | Scikit-learn / Keras |
| Data Storage | JSON (`FoodMenu.json`) |
| Utilities | Custom `utils.py` module |
| Environment | Jupyter Notebook |

---

## 🚀 How to Run Locally

```bash
# 1. Clone the repository
git clone https://github.com/Charu305/Hotel-Chatbot.git
cd Hotel-Chatbot

# 2. Install dependencies
pip install pandas numpy nltk scikit-learn tensorflow jupyter

# 3. Download NLTK resources (first run only)
python -c "import nltk; nltk.download('stopwords'); nltk.download('wordnet')"

# 4. Launch the chatbot notebook
jupyter notebook Hotel-Chatbot.ipynb

# 5. Or import utilities directly
from utils import preprocess_text, get_menu_item
```

---

## 📁 Key Files Explained

| File | Purpose |
|---|---|
| `Hotel-Chatbot.ipynb` | End-to-end pipeline: training data, model training, intent classification, conversation loop |
| `utils.py` | Reusable helper functions — text preprocessing, menu lookup, response formatting |
| `FoodMenu.json` | Structured food menu — easily updated without touching the model |

---

## 💡 Key Learnings & Takeaways

- **Intent classification is the core of any rule-based or hybrid chatbot** — before generating any response, the system must correctly understand *what the user wants*. Accuracy on intent classification directly determines how useful the chatbot is.
- **Modular design matters** — putting preprocessing and helper logic in `utils.py` rather than the notebook makes the code reusable, testable, and easier to maintain. This is production thinking, not just notebook experimentation.
- **Data-driven menu responses beat hardcoded strings** — storing the menu in `FoodMenu.json` means the bot's knowledge can be updated by editing a config file, not by retraining a model. This separation of data from logic is a key software engineering principle.
- **Fallback handling is essential** — a chatbot without a fallback strategy will confidently give wrong answers when it doesn't understand input. A confidence threshold + fallback response is the minimum viable safety net.
- **Training utterance variety drives generalisation** — providing 10–15 diverse phrasings per intent dramatically improves the model's ability to handle real, unpredictable guest messages that don't match training examples exactly.

---

## 🔮 Potential Enhancements

- Integrate with a **Large Language Model (LLM)** for open-domain, context-aware conversations beyond predefined intents
- Add **multi-turn conversation memory** — remembering earlier messages in the session (e.g., "I'll have that" referring to a previously mentioned item)
- Connect to a **real booking system / PMS (Property Management System)** for live room availability
- Deploy as a **WhatsApp / Telegram / Web widget** chatbot using Twilio or Dialogflow

---

## 👩‍💻 Author

**Charunya**
🔗 [GitHub Profile](https://github.com/Charu305)

---

## 📄 License

This project is developed for educational and research purposes.
