import os
import pandas as pd
import matplotlib.pyplot as plt
from googleapiclient.discovery import build
from textblob import TextBlob
from dotenv import load_dotenv
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import streamlit as st

nltk.download('vader_lexicon')

# Set up YouTube API
load_dotenv()
api_key = os.getenv('YOUTUBE_API')  # Replace with your YouTube API key
youtube = build('youtube', 'v3', developerKey=api_key)

# Initialize VADER sentiment intensity analyzer
sia = SentimentIntensityAnalyzer()

def get_id(link=""):
    id = ''
    if link.find('www.youtube.com') != -1:
        id = link.lstrip('https://www.youtube.com/watch?v=')
    elif link.find('youtu.be') != -1:
        strt = link.lstrip('https://youtu.be/')
        ind = strt.find('?')
        id = strt[0:ind]
    return id

# Function to get comments and user details from a YouTube video
def get_video_comments(video_id):
    comments_data = []
    response = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        maxResults=100,  # Fetch up to 100 comments at a time
        textFormat='plainText'
    ).execute()

    while response:
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            author = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
            comments_data.append({'comment': comment, 'author': author})

        # Check if there's another page of comments
        if 'nextPageToken' in response:
            response = youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                pageToken=response['nextPageToken'],
                maxResults=100,
                textFormat='plainText'
            ).execute()
        else:
            break
    return comments_data

# Perform Sentiment Analysis using TextBlob
def get_sentiment(text):
    analysis = TextBlob(text)
    return analysis.sentiment.polarity

# Perform Emotion Analysis using VADER
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

def main():
    st.markdown("""<h1 style="font-weight: bold  "> YouTube Video's Sentiment & Emotion Analyzer</h1> """, unsafe_allow_html=True)
    usr_inp = st.text_input("Please Enter Video Link and Press Enter")
    video_id = get_id(usr_inp)

    col1, col2, col3 = st.columns(3)
    with col1:
        Analyze_butt = st.button("Analyze Video Sentiments ✅")
    with col2:
        pre = st.toggle("Enable Preview")
    with col3:
        st.page_link("./main_page.py", label="Home", icon="🏠")

    if video_id is not '' and Analyze_butt == True:

        if pre == True:
            st.video(usr_inp)

        # Get YouTube comments
        comments_data = get_video_comments(video_id)

        # Convert comments to a DataFrame
        df = pd.DataFrame(comments_data)

        # Sentiment analysis
        df['sentiment'] = df['comment'].apply(get_sentiment)
        df['sentiment_class'] = df['sentiment'].apply(classify_sentiment)

        # Emotion analysis
        df['emotion'] = df['comment'].apply(get_emotion)

        # Sentiment distribution pie chart
        sentiment_counts = df['sentiment_class'].value_counts()

        # Define labels and colors for the pie chart
        labels = sentiment_counts.index
        sizes = sentiment_counts.values
        colors = ['#66b3ff', '#ff6666', '#ffcc99', '#99ff99']  # Colors for Positive, Negative, Mixed, Neutral
        explode = (0.1, 0, 0, 0)  # Explode only the first slice (Positive)

        # Plot the pie chart
        fig, ax = plt.subplots()

        ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, explode=[0.1] * len(sizes), shadow=True, startangle=90)
        st.title('Sentiment Analysis of YouTube Comments')
        ax.axis('equal')  # Equal aspect ratio ensures the pie chart is circular
        st.pyplot(fig)

        # Display emotion distribution
        emotion_counts = df['emotion'].value_counts()
        st.subheader("Emotion Analysis of Comments")
        st.bar_chart(emotion_counts)

        # Display sentiment and emotion for each comment
        st.subheader("Sentiment and Emotion of Each Comment:")
        st.dataframe(df)

    elif video_id is '' and Analyze_butt == True:
        st.error("Please Enter A Link")

if __name__ == "__main__":
    main()