from database import Database

class KnowledgeBase:
    def __init__(self):
        self.init_database()
        
        self.static_knowledgebase = {
            # Greetings
            "hi": [
                "Hello! How can I assist you with your banking needs today?",
                "Hi there! What banking service can I help you with?",
                "Hey! Welcome to Trust Bank. What can I do for you?"
            ],
            "hello": [
                "Hello! Welcome to our banking service. How may I help you?",
                "Hi! What banking query do you have today?",
                "Greetings! I'm your banking assistant. How can I be of service?"
            ],
            "hey": [
                "Hey there! What brings you to Trust Bank today?",
                "Hey! Ready to handle your banking needs. What's on your mind?"
            ],
            
            # Time-based greetings
            "good morning": [
                "Good morning! How can I assist you with your banking today?",
                "Morning! What banking service can I help you with?",
                "Top of the morning to you! What banking matters shall we discuss?"
            ],
            "good afternoon": [
                "Good afternoon! How may I assist you with your banking needs?",
                "Afternoon! What financial service are you looking for today?"
            ],
            "good evening": [
                "Good evening! How can I help with your banking this evening?",
                "Evening! What banking query brings you here tonight?"
            ],
            "thanks": [
                "Anytime! What else can I do for you today?",
                "No problem at all! I'm here if you need more assistance.",
                "You're welcome! Is there anything else I can help you with?",
                "My pleasure! Let me know if you need anything else.",
                "Happy to help! Don't hesitate to ask if you have more questions."
            ],
            
            # Farewells
            "goodbye": [
                "Goodbye! Have a great day!",
                "Farewell! Come back if you have more banking questions.",
                "Take care! Remember we're here 24/7 for your banking needs."
            ],
            "bye": [
                "Bye now! Don't hesitate to return if you need anything.",
                "See you later! Happy banking!"
            ]
        }
        
        # Banking knowledge base
        self.banking_details = {
            "name": "TrustBank",
            "card": ["debit", "credit"],
            "service": ["transfer", "balance", "statement", "payment", "withdrawal"],
            "opening_hours": {
                "from": "8.00 am",
                "to": "8.00 pm"
            },
            "open_days": ["Monday", "Tuesday", "Wednesday","Thursday", "Friday", "Saturday"],
            "close_days": ["Poya Days", "Bank Holidays"],
            "bank app": "TrustBank Banking App",
            "website": "www.trustbank.lk",
            "how to open account": "Visit a branch or to create online visit the website",
            "documents need to open an account": "National ID card/Driving License/Passport",
            "reset PIN of a card": "Visit a branch",
            "how to apply for a loan": "visit closest branch or find the application from our website"
        }

    def init_database(self):
         self.db = Database()