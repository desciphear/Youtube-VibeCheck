import streamlit as st
import requests
import pandas as pd
from dotenv import load_dotenv
from textblob import TextBlob
import os
import nltk
import matplotlib.pyplot as plt
from nltk.sentiment import SentimentIntensityAnalyzer

sia = SentimentIntensityAnalyzer()

code = 0
nltk.download('vader_lexicon')
def inp(pgid, poid):
    page_id = pgid # your page id, ex: '123456789'
    post_id = poid
    
    load_dotenv()
    access_token =os.getenv('FB_TOKEN') # your access token, from https://developers.facebook.com/tools/explorer/

    url = f'https://graph.facebook.com/v21.0/{page_id}_{post_id}/comments?access_token={access_token}'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data["data"])
    else:
        global code
        code = 500
        data = {
    "Name": ["Alice", "Bob", "Charlie"],
    "Age": [25, 30, 35],
    "City": ["New York", "Los Angeles", "Chicago"]
}
        df = pd.DataFrame(data)
    return df

def get_sentiment(text):
    analysis = TextBlob(text)
    return analysis.sentiment.polarity



# Classify sentiment as Positive, Negative, Neutral, or Mixed
def classify_sentiment(polarity):
    if polarity > 0.2:
        return 'Positive'
    elif polarity < -0.2:
        return 'Negative'
    elif -0.2 <= polarity <= 0.2 and polarity != 0:
        return 'Mixed'
    else:
        return 'Neutral'

def get_emotion(text):
    sentiment_scores = sia.polarity_scores(text)
    compound_score = sentiment_scores['compound']

    # Classify emotions based on compound score
    if compound_score >= 0.5:
        return 'Happy'
    elif compound_score <= -0.5:
        return 'Sad'
    elif -0.5 < compound_score < 0.5:
        return 'Neutral'
    else:
        return 'Mixed'


def main():
    st.title("Facebook Post's Comment Analyzer")
    pgid = st.text_input("Enter Page ID")
    poid = st.text_input("Enter Post ID")
    col1, col2 = st.columns(2)
    with col1:
        start = st.button("Analyze")
    with col2:
        st.page_link("./main_page.py",label="Home", icon="🏠")
    if start == True:
        df = inp( pgid, poid)
        
        if code == 500:
            st.markdown('''<h2 style="text-align: center; color: red;"> Invalid Page and/or Post ID🚫</h2>''',unsafe_allow_html=True)
        else:
            df['sentiment'] = df['message'].apply(get_sentiment)
            df['sentiment_class'] = df['sentiment'].apply(classify_sentiment)
            sentiment_counts = df['sentiment_class'].value_counts()
            df['emotion'] = df['message'].apply(get_emotion)

            # Define labels and colors for the pie chart
            labels = sentiment_counts.index
            sizes = sentiment_counts.values
            colors = ['#66b3ff', '#ff6666', '#ffcc99', '#99ff99']  # Colors for Positive, Negative, Mixed, Neutral
            

            # Plot the pie chart
            fig, ax = plt.subplots()
            
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, explode=[0.1] * len(sizes), shadow=True, startangle=90)
            st.title('''Sentiment Analysis of Post's Comments''')
            ax.axis('equal')  # Equal aspect ratio ensures the pie chart is circular
            st.pyplot(fig)

            emotion_counts = df['emotion'].value_counts()
            st.subheader("Emotion Analysis of Comments")
            st.bar_chart(emotion_counts)

            st.subheader("Sentiment and Emotion of Each Comment:")
            st.dataframe(df)
        

if __name__ == "__main__":
    main()