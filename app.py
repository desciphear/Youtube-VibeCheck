import os
import pandas as pd
import matplotlib.pyplot as plt
from googleapiclient.discovery import build
from textblob import TextBlob
from dotenv import load_dotenv
import nltk
import streamlit as st



nltk.download('vader_lexicon')

# Set up YouTube API
load_dotenv()
api_key = os.getenv('YOUTUBE_API')
  # Replace with your YouTube API key
youtube = build('youtube', 'v3', developerKey=api_key)

def get_id(link=""):

    link = repr(link)

    id=''
        
    if link.find('https://www.youtube.com/watch')  is not -1:
        id = link[33:-1]
        print(id)
            
    elif link.find('https://youtu.be/') is not -1:        
        id = link[18:29]
        print(id)
    
    elif link.find('https://www.youtube.com/shorts') is not -1:
        id = link[32:-1]
        print(id)

    elif link.find('https://youtube.com/shorts') is not -1:
        id = link[28:39]
        print(id)
    
    
    
    return id 




# Function to get comments and user details from a YouTube video
def get_video_comments(video_id):
    try:
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
    except Exception as ex:
        print(ex)
        comments_data.append({'comment': 'None', 'author': 'None'}) 
    return comments_data





# Perform Sentiment Analysis using TextBlob
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





def main():
    st.markdown("""<h1 style="font-weight: bold  "> YouTube VibeCheck</h1> """, unsafe_allow_html=True)
    usr_inp = st.text_input("Please Enter Video Link and Press Enter")

    video_id = get_id(usr_inp)

   

    
    
    col1, col2 = st.columns(2)
    with col1:
        Analyze_butt = st.button("Analyze Video Sentiments ✅")
    with col2:
        pre = st.toggle("Enable Preview")

    
    

    if video_id is not '' and Analyze_butt == True:
        
        if pre == True:
            if usr_inp.find('shorts') is not -1:
                st.markdown("""<h2 style="text-align: center; color: red;"> No Preview Available For shorts🚫</h2>""", unsafe_allow_html=True)
            
            else:
                st.video(usr_inp)

   
        # Get YouTube comments
        comments_data = get_video_comments(video_id)

        # Convert comments to a DataFrame
        df = pd.DataFrame(comments_data)

       

        df['sentiment'] = df['comment'].apply(get_sentiment)

        df['sentiment_class'] = df['sentiment'].apply(classify_sentiment)



        # Save the DataFrame to a CSV file (optional)
        

        # Sentiment distribution pie chart
        sentiment_counts = df['sentiment_class'].value_counts()

        # Define labels and colors for the pie chart
        if df.iat[0,0] != 'None' and df.iat[0,1] != 'None':
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
            st.dataframe(df)
        
        else: 
            st.markdown("""<h2 style="text-align: center; color: red;"> Invalid Link Provided🚫</h2>""", unsafe_allow_html=True)

    elif video_id is '' and Analyze_butt == True:
        st.error("Please Enter A Valid Link")


if __name__ == "__main__":
    main()
    
