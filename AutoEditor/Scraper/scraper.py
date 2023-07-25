import requests


def extract_video_info_pexels(video, keyword):
    return {
        'keyword': keyword,
        'url': video['video_files'][0]['link'],
        'quality': video['video_files'][0]['quality'],
        'duration': video['duration']
    }


def extract_video_info_pixabay(video, keyword):
    return {
        'keyword': keyword,
        'url': video['videos']['medium']['url'],
        'quality': 'medium',
        'duration': video['duration']
    }


def get_videos_from_pexels(keyword, pexels_api_key):
    url = "https://api.pexels.com/videos/search"
    querystring = {"query": keyword, "per_page": "5", "orientation": "landscape", "size": "medium"}
    headers = {'Authorization': pexels_api_key}
    response = requests.request("GET", url, headers=headers, params=querystring)

    if response.status_code != 200:
        print(f"Requête Pexels API échouée avec le statut {response.status_code}")
        return []

    data = response.json()
    if 'videos' not in data:
        print(f"Pas de vidéos trouvées pour le keyword {keyword}")
        return []

    videos = data['videos']
    return [extract_video_info_pexels(video, keyword) for video in videos]


def get_videos_from_pixabay(keyword, pixabay_api_key):
    url = "https://pixabay.com/api/videos/"
    querystring = {"key": pixabay_api_key, "q": keyword, "video_type": "film", "per_page": "5", "orientation": "horizontal", "video_quality": "720"}
    response = requests.request("GET", url, params=querystring)
    videos = response.json()['hits']
    return [extract_video_info_pixabay(video, keyword) for video in videos]


def get_videos_for_keywords(keywords, pexels_api_key, pixabay_api_key):
    videos = []
    for keyword in keywords:
        videos.extend(get_videos_from_pexels(keyword, pexels_api_key))
        videos.extend(get_videos_from_pixabay(keyword, pixabay_api_key))
    return videos
