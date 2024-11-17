from dotenv import load_dotenv
load_dotenv()

import os
import streamlit as st
import google.generativeai as genai
from googleapiclient.discovery import build
import re

##configuring genai and yt
genai.configure(api_key=os.getenv("GEMINI_API"))
youtube = build('youtube','v3',developerKey=os.getenv("YOUTUBE_API")) ##youtube object now represents the YOUTUBE API client that allows us to make request to the YouTube Data API

input_prompt = """
You are an expert song trend analyser. you predict on if the song will go in trend or viral in the shortform content  like reels,tiktok,shorts,etc. you predict by analysing the data of the video. like likes,dislikes,like dislike ratio with reference to the views. number of comments.types of comments like funny,making fun of the song,supportive,loving,bad,crticising by reading the top comments. and then giving your final answer in terms of percentage and a small justification
"""


def get_video_data(video_id):
    ##youtbe.videos().list() is a method to request information about a specific video
    ##part specifies which data i want to retrieve
    ##snippet basic video details such as title,descriptions,tags,etc
    ##contentDetails information like duration,upload date,etc
    ##statistics data like view count,like count,dislike count etc
    request = youtube.videos().list(
        part = 'snippet,contentDetails,statistics',
        id = video_id
        )
    response = request.execute()##sends request to the api server, returns the data in the below format
    try :
        video_info = response["items"][0]
    except IndexError :
        st.write("No data fetched")
    data = {
            "title" : video_info["snippet"]["title"],
            "published_at" : video_info["snippet"]["publishedAt"],
            "view_count" : video_info["statistics"].get("viewCount","N/A"), ##.get() is used as view count may always be not available... so if view count is not available then it will return N/A... .get() is not used for other values because those values will be surely extracted
            "like_count" : video_info["statistics"].get("likeCount","N/A"),
            "dislike_count" : video_info["statistics"].get("dislikeCount","N/A"),
            "comment_count" : video_info["statistics"].get("commentCount","N/A")
        }
    return data


##streamlit
st.set_page_config(page_title="Trendly")
st.title("Song Trend Analyser")
YTlink = st.text_input("Enter Video URL : ",key="input")
pattern = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed\/|v\/|e\/|watch\?v%3D|.+\/)([a-zA-Z0-9_-]{11})' ##regex for yt video link
if st.button("Analyse") :
    if re.match(pattern,YTlink):
        video_id = YTlink.split("=")[1]
        st.image(f"https://img.youtube.com/vi/{video_id}/0.jpg",use_container_width=True)
        video_data = get_video_data(video_id)
        if video_data :
            st.subheader("Video Details")
            st.write(f"**Title:** {video_data['title']}")
            st.write(f"**Published At:** {video_data['published_at']}")
            st.write(f"**Views:** {video_data['view_count']}")
            st.write(f"**Likes:** {video_data['like_count']}")
            st.write(f"**Dislikes:** {video_data['dislike_count']}")
            st.write(f"**Comments:** {video_data['comment_count']}")
        else:
            st.error("Failed to fetch video data")