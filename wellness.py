#!/usr/bin/env python
# coding: utf-8

import streamlit as st
import pandas as pd
import datetime
import altair as alt
import os

# Predefined list of players
PLAYER_LIST = [
    "John Smith", 
    "Emma Rodriguez", 
    "Michael Johnson", 
    "Sophia Lee", 
    "David Kim", 
    "Olivia Chen", 
    "Carlos Mendez", 
    "Aisha Patel", 
    "Ryan Thompson", 
    "Isabella Garcia"
]

# Set page configuration
st.set_page_config(page_title="Player Wellness Tracker", layout="wide")

# Initialize session state variables if they don't exist
if 'data' not in st.session_state:
    if os.path.exists('wellness_data.csv'):
        st.session_state.data = pd.read_csv('wellness_data.csv')
    else:
        # Create empty dataframe with necessary columns
        st.session_state.data = pd.DataFrame(columns=[
            'player_name', 'date', 'sleep_quality', 'soreness_level', 
            'energy_level', 'readiness_score', 'additional_questions'
        ])

# Function to save data
def save_data():
    st.session_state.data.to_csv('wellness_data.csv', index=False)

# Function to apply color styling to low scores
def color_low_scores(val):
    """
    Color cells red if the score is less than 5
    """
    color = 'background-color: red; color: white;' if val < 5 else ''
    return color

# Create sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Submit Response", "View Results"])

if page == "Submit Response":
    # [Previous Submit Response code remains the same]
    st.title("Daily Wellness Check-in")
    st.subheader("Track your daily readiness and recovery")
    
    # Date selection with default to today
    date = st.date_input("Date", datetime.date.today())
    
    # Player selection with dropdown
    player_name = st.selectbox("Select your name", PLAYER_LIST)
    
    # Questions
    st.header("Today's Check-in Questions")
    
    sleep_quality = st.slider(
        "Q1: How did you sleep last night?", 
        1, 10, 5, 
        help="1 = Very poor, 10 = Excellent"
    )
    
    soreness_level = st.slider(
        "Q2: How sore are you?", 
        1, 10, 5, 
        help="1 = Extremely sore, 10 = No soreness"
    )
    
    energy_level = st.slider(
        "Q3: How would you rate your energy level?", 
        1, 10, 5, 
        help="1 = Very low energy, 10 = High energy"
    )
    
    readiness_score = st.slider(
        "Q4: How would you score your readiness?", 
        1, 10, 5, 
        help="1 = Not ready to train, 10 = Fully ready"
    )
    
    # Additional Custom Questions Section
    st.header("Additional Questions (Optional)")
    
    # Checkbox to enable additional questions
    add_custom_questions = st.checkbox("Add Custom Questions")
    
    additional_questions_data = {}
    if add_custom_questions:
        # Number of custom questions
        num_questions = st.number_input(
            "How many additional questions do you want to add?", 
            min_value=1, 
            max_value=5, 
            value=1
        )
        
        for i in range(num_questions):
            question = st.text_input(f"Custom Question {i+1}")
            
            # Choose input type
            input_type = st.selectbox(
                f"Input Type for Question {i+1}", 
                ["Slider (1-10)", "Text Response", "Yes/No"]
            )
            
            if input_type == "Slider (1-10)":
                response = st.slider(
                    f"Rate {question}", 
                    1, 10, 5, 
                    help="1 = Lowest, 10 = Highest"
                )
            elif input_type == "Text Response":
                response = st.text_area(f"Response for: {question}")
            else:  # Yes/No
                response = st.radio(f"{question}", ["Yes", "No"])
            
            additional_questions_data[question] = response
    
    # Submit button
    if st.button("Submit"):
        # Prepare additional questions data for storage
        additional_questions_str = str(additional_questions_data) if additional_questions_data else "None"
        
        # Add new data
        new_data = pd.DataFrame({
            'player_name': [player_name],
            'date': [date.strftime('%Y-%m-%d')],
            'sleep_quality': [sleep_quality],
            'soreness_level': [soreness_level],
            'energy_level': [energy_level],
            'readiness_score': [readiness_score],
            'additional_questions': [additional_questions_str]
        })
        
        # Append to existing data
        st.session_state.data = pd.concat([st.session_state.data, new_data], ignore_index=True)
        save_data()
        
        st.success(f"Thank you {player_name}! Your response has been recorded.")

elif page == "View Results":
    st.title("Player Wellness Results")
    
    # Check if there's data
    if st.session_state.data.empty:
        st.warning("No wellness data available. Please submit some responses first.")
    else:
        # Prepare data for display
        display_data = st.session_state.data.copy()
        
        # Style the data to highlight low scores
        styled_data = display_data.style.applymap(color_low_scores, subset=[
            'sleep_quality', 
            'soreness_level', 
            'energy_level', 
            'readiness_score'
        ])
        
        # Display the table
        st.dataframe(display_data.style.applymap(color_low_scores, subset=[
            'sleep_quality', 
            'soreness_level', 
            'energy_level', 
            'readiness_score'
        ]))
        
        # Optional: Aggregate statistics
        st.header("Team Summary")
        
        # Calculate average scores
        avg_scores = display_data[['sleep_quality', 'soreness_level', 'energy_level', 'readiness_score']].mean()
        st.write("Average Scores:")
        st.dataframe(avg_scores)
        
        # Count of low scores (less than 5)
        low_score_counts = (display_data[['sleep_quality', 'soreness_level', 'energy_level', 'readiness_score']] < 5).sum()
        st.write("Number of Low Scores (< 5):")
        st.dataframe(low_score_counts)
        
        # Optional: Filter for athletes with low scores
        st.header("Athletes with Low Scores")
        low_score_threshold = st.slider("Low Score Threshold", min_value=1, max_value=5, value=3)
        
        # Find athletes with any score below the threshold
        low_score_athletes = display_data[
            (display_data['sleep_quality'] < low_score_threshold) |
            (display_data['soreness_level'] < low_score_threshold) |
            (display_data['energy_level'] < low_score_threshold) |
            (display_data['readiness_score'] < low_score_threshold)
        ]
        
        st.dataframe(low_score_athletes.style.applymap(color_low_scores, subset=[
            'sleep_quality', 
            'soreness_level', 
            'energy_level', 
            'readiness_score'
        ]))