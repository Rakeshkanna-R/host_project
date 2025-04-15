from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
import os
import streamlit as st

# Set up Google API credentials
os.environ["GOOGLE_API_KEY"] = "AIzaSyB97vycGzxXT-BCLaS-aUFAOtmIxIWCUxI"

# Initialize the user database in session state if it doesn't exist
if "user_db" not in st.session_state:
    st.session_state.user_db = {}  # Default user database

# Session state initialization for authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Define the function to generate the travel plan
def generate_response(destination, number_of_days, budget):
    try:
        # Validate inputs
        if not isinstance(number_of_days, (int, float)) or number_of_days <= 0:
            raise ValueError("Number of days must be a positive number.")
        if not isinstance(budget, (int, float)) or budget <= 0:
            raise ValueError("Budget must be a positive number.")

        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful assistant that plans trips based on the user's destination, number of days, and budget.",
                ),
                (
                    "human",
                    f"Plan my trip to {destination}. I want to stay for {number_of_days} days and my budget is ${budget}. Please suggest Accommodation, Food, Transportation, Tips for Saving Money, some activities to do, and places to visit with a suitable title. Format the response in clear sections with bullet points or numbered lists for easy reading.",
                ),
            ]
        )
        chain = prompt | llm
        ai_response = chain.invoke({"destination": destination, "number_of_days": number_of_days, "budget": budget})
        return ai_response.content if hasattr(ai_response, "content") else str(ai_response)
    except Exception as e:
        st.error(f"Error generating travel plan: {str(e)}")
        return None

# Authentication functions
def login(username, password):
    if st.session_state.user_db.get(username) == password:
        st.session_state.authenticated = True
        st.session_state.username = username
        st.success("Login successful!")
    else:
        st.error("Invalid username or password.")

def signup(username, password):
    if username in st.session_state.user_db:
        st.error("Username already exists. Please choose a different one.")
    else:
        st.session_state.user_db[username] = password
        st.success("Signup successful! Please log in.")

# Streamlit UI setup
st.set_page_config(page_title="Travel Planner", page_icon=":earth_africa:")

# Login and Signup page layout
if not st.session_state.authenticated:
    st.sidebar.title("Login / Signup")
    option = st.sidebar.selectbox("Choose option", ["Login", "Signup"])

    if option == "Login":
        st.sidebar.subheader("Login")
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            login(username, password)

    elif option == "Signup":
        st.sidebar.subheader("Signup")
        new_username = st.sidebar.text_input("Create Username")
        new_password = st.sidebar.text_input("Create Password", type="password")
        if st.sidebar.button("Signup"):
            signup(new_username, new_password)
else:
    st.sidebar.write(f"Welcome, {st.session_state.username}")
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.rerun()

# Travel planner UI
if st.session_state.authenticated:
    st.title("Your Personalized Trip Planner")
    st.header("Let AI Create the Perfect Trip for You")

    # Input fields with validation
    destination = st.text_input("Enter your travel destination:", key="destination")
    number_of_days = st.number_input("Enter number of days for the trip:", min_value=1, key="days")
    budget = st.number_input("Enter your budget (e.g., $2000):", min_value=1.0, key="budget")

    if st.button("Generate Travel Plan") and destination.strip() and number_of_days and budget:
        with st.spinner("Generating travel plan..."):
            response = generate_response(destination, number_of_days, budget)
            if response:
                st.markdown(response)
            else:
                st.error("Failed to generate the travel plan. Please try again.")
else:
    st.title("Please log in to access the Trip Planner.")
