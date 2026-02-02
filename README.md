# 🛒 AI E-Commerce Bot

A smart chatbot application built with **Python** and **Streamlit** that assists users with e-commerce queries. This project uses the **Groq API** (Llama 3 model) to generate intelligent, streaming responses.

## 🚀 Features
* **AI-Powered:** Utilizes the `llama-3.3-70b-versatile` model for high-quality responses.
* **Real-time Streaming:** Responses appear instantly as they are generated.
* **Context Aware:** Maintains chat history for a natural conversation flow.
* **Secure:** Uses environment variables to protect API keys.

## 🛠️ Tech Stack
* **Frontend:** Streamlit
* **AI Model:** Groq API (Llama 3)
* **Language:** Python 3.x

## ⚙️ Setup & Installation

Follow these steps to run the project locally.

### 1. Clone the repository
```bash
git clone [https://github.com/Ritheshcool/ecommerce-bot.git](https://github.com/Ritheshcool/ecommerce-bot.git)
cd ecommerce-bot
2. Create a Virtual Environment (Optional but Recommended)
# Windows
python -m venv .venv
.venv\Scripts\activate

# Mac/Linux
python3 -m venv .venv
source .venv/bin/activate
3. Install Dependencies
pip install -r requirements.txt
4. Set up Environment Variables
Create a file named .env in the root directory and add your Groq API key:
GROQ_API_KEY=your_actual_api_key_here
5. Run the App
streamlit run app.py
📂 Project Structure
ecommerce-bot/
├── .venv/            # Virtual environment (ignored by Git)
├── .env              # API keys (ignored by Git)
├── .gitignore        # Files to ignore
├── app.py            # Main application code
├── requirements.txt  # List of dependencies
└── README.md         # Project documentation
