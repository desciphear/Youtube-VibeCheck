import os
import pandas as pd
import matplotlib.pyplot as plt
from googleapiclient.discovery import build
from textblob import TextBlob
from dotenv import load_dotenv
import nltk

# Download necessary NLTK data (optional)
nltk.download('vader_lexicon')

# Set up YouTube API
load_dotenv()
api_key = os.getenv('YOUTUBE_API')
  # Replace with your YouTube API key
youtube = build('youtube', 'v3', developerKey=api_key)

def get_id(link=""):


    id=''
        
    if link.find('www.youtube.com')  is not -1 :    
        id = link.lstrip('https://www.youtube.com/watch?v=')

    elif link.find('youtu.be') is not -1:
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

#video link
link = input("Enter YouTube Video Link")

# Example video ID (replace with your own)
video_id = get_id(link)
print(video_id)

# Get YouTube comments
comments_data = get_video_comments(video_id)

# Convert comments to a DataFrame
df = pd.DataFrame(comments_data)

# Perform Sentiment Analysis using TextBlob
def get_sentiment(text):
    analysis = TextBlob(text)
    return analysis.sentiment.polarity

df['sentiment'] = df['comment'].apply(get_sentiment)

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

df['sentiment_class'] = df['sentiment'].apply(classify_sentiment)

# Save the DataFrame to a CSV file (optional)
csv_file_name = 'youtube_comments_sentiment.csv'
df.to_csv(csv_file_name, index=False)
print(f"CSV file saved as {csv_file_name}")

# Sentiment distribution pie chart
sentiment_counts = df['sentiment_class'].value_counts()

# Define labels and colors for the pie chart
labels = sentiment_counts.index
sizes = sentiment_counts.values
colors = ['#66b3ff', '#ff6666', '#ffcc99', '#99ff99']  # Colors for Positive, Negative, Mixed, Neutral
explode = (0.1, 0, 0, 0)  # Explode only the first slice (Positive)

# Plot the pie chart
plt.figure(figsize=(7, 7))
plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, explode=[0.1] * len(sizes), shadow=True, startangle=90)
plt.title('Sentiment Analysis of YouTube Comments')
plt.axis('equal')  # Equal aspect ratio ensures the pie chart is circular
plt.show()