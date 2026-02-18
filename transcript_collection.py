from youtube_transcript_api import YouTubeTranscriptApi

def get_transcript(video_id):
    try:
        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id)

        text = " ".join([item.text for item in transcript])
        return text
    except Exception as e:
        return str(e)

# Example Usage
video_url = "https://www.youtube.com/watch?v=53yPfrqbpkE"
video_id = video_url.split("v=")[1]

print(get_transcript(video_id))