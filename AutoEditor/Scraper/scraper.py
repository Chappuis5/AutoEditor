import requests

def get_videos_from_pexels(keyword):
    url = "https://api.pexels.com/videos/search"
    querystring = {"query": keyword, "per_page": "5", "orientation": "landscape", "size": "medium"}
    headers = {'Authorization': 'Votre clé API Pexels'}
    response = requests.request("GET", url, headers=headers, params=querystring)
    return response.json()

def get_videos_from_pixabay(keyword):
    url = "https://pixabay.com/api/videos/"
    querystring = {"key": "Votre clé API Pixabay", "q": keyword, "video_type": "film", "per_page": "5", "orientation": "horizontal", "video_quality": "720"}
    response = requests.request("GET", url, params=querystring)
    return response.json()

def get_videos_for_keywords(keywords):
    videos = []
    for keyword in keywords:
        videos.extend(get_videos_from_pexels(keyword))
        videos.extend(get_videos_from_pixabay(keyword))
    return videos
