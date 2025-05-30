import os
import re
import random
import pickle
import datetime
import logging
import openai
from openai import OpenAI
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from knowledgebase import KnowledgeBase
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class Chatbot: 
    def __init__(self):
        self.knowledgebase = KnowledgeBase()
        
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        self.model_path = 'chatbot_ml_model.pkl'
        self.vectorizer_path = 'vectorizer.pkl'
        self.initialize_ml_component()
        
        # these are for UI
        self.last_user_query = ""
        self.last_chatbot_response = ""
        
        # open ai
        self.client = OpenAI()
        self.client.api_key = os.getenv('OPENAI_API_KEY')
        
        # converstation history
        self.conversation_history = []
    
    def add_conversation(self, message):
        self.conversation_history.append(message)
        if len(self.conversation_history) == 12:
            del self.conversation_history[:6]
    
    def get_response_from_openai(self, message):
        try:
            completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a banking assistant and you only respond using the detail provided. If the query is unrelated to bank, say 'Sorry, I can only answer bank related questions'."},
                    {"role": "system", "content": f"Here are some of the details about the bank:\n {self.knowledgebase.banking_details}"},
                    *self.conversation_history,
                    {"role": "user", "content": f"{message}"}
                ]    
            )
            self.add_conversation({"role": "user", "content": f"{message}"})
            response = completion.choices[0].message.content.strip()
            self.add_conversation({"role": "assistant", "content": f"{response}"})
            return response

        except openai.APIConnectionError as e:
            logging.error(f"Connection error: {e}")
            return "Sorry, I'm having trouble connecting to the response engine. Please try again later."

        except openai.RateLimitError as e:
            logging.warning(f"Rate limit hit: {e}")
            return "Sorry, I'm receiving too many requests at the moment. Please try again in a few seconds."

        except openai.AuthenticationError as e:
            logging.critical(f"Authentication failed: {e}")
            return "Authentication with the AI service failed. Please contact support."

        except openai.OpenAIError as e:
            logging.error(f"OpenAI error: {e}")
            print(self.conversation_history)
            return "Sorry, something went wrong while processing your request."

        except Exception as e:
            logging.exception(f"Unexpected error: {e}")
            return "An unexpected error occurred. Please try again later."
        
    def fix_typos_and_grammer(self, query):
        try:
            print(f"Query -> {query}")
            completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "If there are any typoes and grammer errors in the query fix them, but don't change the query, and just send the query no additional words. If a single word is sent, just fixed typos if there is any, and return the word only"},
                    {"role": "user", "content": f"{query}"}
                ]    
            )
            return completion.choices[0].message.content.strip()

        except openai.APIConnectionError as e:
            logging.error(f"Connection error: {e}")
            return "Sorry, I'm having trouble connecting to the response engine. Please try again later."

        except openai.RateLimitError as e:
            logging.warning(f"Rate limit hit: {e}")
            return "Sorry, I'm receiving too many requests at the moment. Please try again in a few seconds."

        except openai.AuthenticationError as e:
            logging.critical(f"Authentication failed: {e}")
            return "Authentication with the AI service failed. Please contact support."

        except openai.OpenAIError as e:
            logging.error(f"OpenAI error: {e}")
            return "Sorry, something went wrong while processing your request."

        except Exception as e:
            logging.exception(f"Unexpected error: {e}")
            return "An unexpected error occurred. Please try again later."
        
    def initialize_ml_component(self):
        print('Initializing ML Model...')
        # Load model if exists
        if os.path.exists(self.model_path) and os.path.exists(self.vectorizer_path):
            with open(self.model_path, 'rb') as f:
                self.ml_model = pickle.load(f)
            with open(self.vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
        else:
            # Initialize a new model
            self.vectorizer = TfidfVectorizer()
            self.ml_model = {}
                     
            self.__save_ml_model()
        print('Completed initializing ML Model')
        
    def __save_ml_model(self):
        print('Saving current ML Model to disk...')
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.ml_model, f)
        with open(self.vectorizer_path, 'wb') as f:
            pickle.dump(self.vectorizer, f)
        print('Completed Saving current ML Model to disk')
        
    # returns the string that only contains the words that in base form
    def preprocess_text(self, text):
        text = text.lower()
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text) # remove special characters
        tokens = word_tokenize(text)
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens if token not in self.stop_words] # Stop words remove
        return ' '.join(tokens)
        
    def find_similar_question_from_model(self, query):
        if not self.ml_model:
            return None
        SIMILARITY_THRESHOLD = 0.9
        processed_query = self.preprocess_text(query)
        query_vec = self.vectorizer.transform([processed_query])
        
        # Calculate similarities with the questions in the
        similarities = {}
        for known_query in self.ml_model:
            known_vec = self.vectorizer.transform([known_query])
            sim = cosine_similarity(query_vec, known_vec)[0][0]
            similarities[known_query] = sim
        
        # Return most similar question
        if similarities:
            best_match = max(similarities.items(), key=lambda x: x[1])
            if best_match[1] > SIMILARITY_THRESHOLD: 
                return best_match[0]
        
        return None
    
    def train_model_from_feedback(self, query, response, feedback):
        MINIMUM_POSITIVE_FEEDBACK_LEVEL = 3
        processed_query = self.preprocess_text(query)
        
        timestamp = datetime.datetime.now().isoformat()
        self.knowledgebase.db.add_data_to_feedback_table(
            query=query,
            response=response,
            feedback=feedback,
            timestamp=timestamp
        )
        
        # Update ML model
        if feedback > MINIMUM_POSITIVE_FEEDBACK_LEVEL:
            if processed_query not in self.ml_model:
                self.ml_model[processed_query] = response
                all_queries = list(self.ml_model.keys()) + [processed_query]
                self.vectorizer.fit(all_queries)
                self.__save_ml_model()
    
    def handle_query(self, query):
        try:
            # Check for similar question from model
            similar_question = self.find_similar_question_from_model(query)
            if similar_question:
                self.add_conversation({"role": "user", "content": f"{query}"})
                response_from_model = self.ml_model[similar_question]
                self.add_conversation({"role": "assistant", "content": f"{response_from_model}"})
                print('Simillar question found')
                return response_from_model

            # check keywords related to accoutns
            if any(word in query.lower() for word in ["account", "accounts", "savings", "checking", "deposit", "fixed deposits", "fix deposits", "fixed"]):
                return self.handle_account_related_query(query)
            
            # Check keywords relateed to loadn
            elif any(word in query.lower() for word in ["loan", "borrow", "mortgage", "finance"]):
                return self.handle_loan_related_query(query)

            # Check keywords related to branch
            elif any(word in query.lower() for word in ["branch", "branches", "branch code", "branch address", "address"]):
                return self.handle_account_related_query(query)

            # Handle general query
            return self.get_response_from_openai(query)

        except Exception as e:
            logging.exception(f"Error while handling banking query: {e}")
            return "Something went wrong while processing your banking question. Please try again later."

    def handle_account_related_query(self, query):       
        try:
            accounts = self.knowledgebase.db.get_all_account_types()
            
            if not accounts:
                return "Sorry, I couldn't find any account information at the moment."

            # format account details
            account_details = "\n".join([
                f"- {account[0]}: {account[1]} (Min balance: ${account[2]}, Interest rate: {account[3]}%)"
                for account in accounts
            ])
            
            updated_query = (
                f"{query}\n\nHere is the list of available bank accounts:\n{account_details}"
            )
            # Use OpenAI to generate a response
            return self.get_response_from_openai(updated_query)
        
        except Exception as e:
            logging.exception(f"Error while handling account query: {e}")
            return "An error occurred while processing your account query. Please try again later."
        
    def handle_branch_related_query(self, query):
        try:
            branches = self.knowledgebase.db.get_all_branches()
            
            if not branches:
                return "Sorry, I couldn't find any branch information at the moment."

            # Format branch details
            branch_details = "\n".join([
                f"- {branch[0]} (Code: {branch[1]}) located at {branch[2]}"
                for branch in branches
            ])
            
            update_query = (
                f"{query}\n\nHere is the list of our bank branches:\n{branch_details}"
            )
            # Use OpenAI to generate a response
            return self.get_response_from_openai(update_query)
        
        except Exception as e:
            logging.exception(f"Error while handling branch query: {e}")
            return "An error occurred while processing your branch query. Please try again later."
                
                
    def handle_loan_related_query(self, query):
        try:
            loans = self.knowledgebase.db.get_all_loan_types()
            
            if not loans:
                return "Sorry, I couldn't find any loan information at the moment."

            # Format loan details
            loan_details = "\n".join([
                f"- {loan[0]}: {loan[1]} (Interest rate: {loan[2]}%, Max amount: ${loan[3]:,.0f}, Term: {loan[4]}–{loan[5]} years)"
                for loan in loans
            ])
            updated_query = (
                f"{query}\n\nHere is the list of our available loan types:\n{loan_details}"
            )
            # Use OpenAI to generate a response
            return self.get_response_from_openai(updated_query)
        
        except Exception as e:
            logging.exception(f"Error while handling loan query: {e}")
            return "An error occurred while processing your loan query. Please try again later."
    
    def generate_response(self, query):
        # Fix grammer
        typo_and_grammer_fixed_query = self.fix_typos_and_grammer(query)
        print(typo_and_grammer_fixed_query)
        
        processed_query = self.preprocess_text(typo_and_grammer_fixed_query)
        
        # check if the query pattern exists in the static knowledgebase
        for pattern, responses in self.knowledgebase.static_knowledgebase.items():
            if processed_query.strip() == pattern.strip():
                return random.choice(responses)

        response = self.handle_query(typo_and_grammer_fixed_query)
        
        return response