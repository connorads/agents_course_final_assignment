from youtube_transcript_api import YouTubeTranscriptApi

def get_youtube_transcript(video_id: str) -> str:
    """
    Fetches the transcript for a given YouTube video ID.

    Args:
        video_id: The ID of the YouTube video.

    Returns:
        The transcript of the video as a string, or an error message if the transcript cannot be fetched.
    """
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_generated_transcript(['en'])
        fetched_transcript = transcript.fetch()
        return " ".join([segment['text'] for segment in fetched_transcript])
    except Exception as e:
        return f"Error fetching transcript: {str(e)}" 