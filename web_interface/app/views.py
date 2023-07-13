from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from threading import Thread
from AutoEditor.Brain.brain import Helper
from AutoEditor.Logger.logger import Logger
from AutoEditor.Scraper.scraper import get_videos_for_keywords
import json
from django.http import HttpResponse, JsonResponse
import os


logger = Logger('AutoEditor.log')


def load_api_keys(config_file):
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        logger.write('Fichier de configuration non trouvé. Veuillez le vérifier.', 'error')
        return None


config = load_api_keys('config.json')


def index(request):

    logger.write('Accéder à l\'index.', 'info')
    if request.method == 'POST':
        logger.write('Formulaire POST reçu.', 'info')
        audio_file = request.FILES['audio']
        script_file = request.FILES['script']

        fs = FileSystemStorage(location='./uploads')
        audio_filename = fs.save(audio_file.name, audio_file)
        script_filename = fs.save(script_file.name, script_file)

        audio_path = fs.path(audio_filename)
        script_path = fs.path(script_filename)

        logger.write('Début du traitement en arrière-plan.', 'info')
        thread = Thread(target=run_transcription_script, args=(audio_path, script_path))
        thread.start()

        return redirect('processing')
    return render(request, 'index.html')


def video_selection(request):
    logger.write('Accéder à la sélection de vidéos.', 'info')

    # Retrieve selected keywords from session
    selected_keywords = request.session.get('selected_keywords', None)

    if not selected_keywords:
        return redirect('index')  # Redirect to index if there's no selected keywords

    logger.write(f'Keywords sélectionnés: {selected_keywords}', 'info')

    # Read the JSON file and extract the videos
    try:
        with open('parts_keywords_times.json', 'r') as f:
            parts_keywords_times = json.load(f)
    except FileNotFoundError:
        logger.write('Le fichier JSON n\'a pas été trouvé, rediriger vers index.', 'info')
        return redirect('index')

    # Combine all the videos from all parts into a single list
    videos = []
    for part in parts_keywords_times:
        if 'videos' in part:
            videos.extend(part['videos'])

    logger.write(f'Vidéos récupérées pour les keywords: {videos}', 'info')

    videos_json = json.dumps(videos)

    context = {
        'videos_json': videos_json,
    }

    return render(request, 'video_selection.html', context)

def processing(request):
    logger.write('Accéder au processing.', 'info')

    if os.path.isfile('parts_keywords_times.json'):
        logger.write('Le fichier JSON existe, rediriger vers keywords.', 'info')
        response = JsonResponse({'redirect': '/keywords/'})  # Return a JSON response
    else:
        logger.write('Le fichier JSON n\'existe pas encore, rester sur processing.', 'info')
        response = render(request, 'processing.html')

    # Add no-cache headers
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'

    return response


def run_transcription_script(audio_path, script_path):
    open_ai_key = config['OPENAI_API_KEY']
    logger.write(f'Open AI KEY used: {open_ai_key}', 'info')
    # Check if the JSON file exists and delete it before processing
    if os.path.isfile('parts_keywords_times.json'):
        os.remove('parts_keywords_times.json')
        logger.write('Ancien fichier JSON supprimé.', 'info')

    options = {
        "audio_path": audio_path,
        "script_path": script_path
    }
    logger.write('Début de la génération des Keywords...', 'info')
    parts_keywords_times = Helper(options, logger, open_ai_key)
    logger.write('Génération des Keywords terminée', 'info')
    with open('parts_keywords_times_temp.json', 'w') as f:
        json.dump(parts_keywords_times, f)

    os.rename('parts_keywords_times_temp.json', 'parts_keywords_times.json')
    logger.write('Fichier JSON renommé, le traitement est terminé.', 'info')


def keywords(request):
    logger.write('Accéder aux keywords.', 'info')
    try:
        with open('parts_keywords_times.json', 'r') as f:
            parts_keywords_times = json.load(f)
        logger.write('Fichier JSON chargé avec succès.', 'info')
        return render(request, 'keywords.html', {'parts_keywords_times': parts_keywords_times})
    except FileNotFoundError:
        logger.write('Le fichier JSON n\'a pas été trouvé, rediriger vers index.', 'info')
        return redirect('index')


def save_keywords(request):
    pexels_api_key = config['PEXELS_API_KEY']
    pixabay_api_key = config['PIXABAY_API_KEY']
    logger.write(f'PEXELS and PIXABAY API KEYS used: {pexels_api_key}, {pixabay_api_key}', 'info')
    logger.write('Sauvegarder les keywords.', 'info')
    if request.method == 'POST':
        selected_keywords = {}
        for part in request.POST.keys():
            if part != "csrfmiddlewaretoken":  # Ignore the csrf token
                if part.startswith('customKeyword'):  # This is a custom keyword
                    custom_keyword = request.POST.get(part)
                    if custom_keyword:  # Ignore if the field is empty
                        part_name = part.replace('customKeyword', 'part')  # Get the corresponding part name
                        if part_name not in selected_keywords:  # Create the list if it doesn't exist yet
                            selected_keywords[part_name] = []
                        selected_keywords[part_name].append(custom_keyword)  # Add the custom keyword to the list
                else:
                    selected_keywords[part] = request.POST.getlist(part)  # Get the selected keywords for this part

        logger.write(f'Keywords sélectionnés: {selected_keywords}', 'info')
        request.session['selected_keywords'] = selected_keywords  # Sauvegarde selected_keywords dans la session
        logger.write(f'Sauvegardé selected_keywords dans la session: {selected_keywords}', 'info')  # Nouveau log

        # Update the JSON file with the new selected keywords
        with open('parts_keywords_times.json', 'r+') as f:
            parts_keywords_times = json.load(f)

            for part, keywords in selected_keywords.items():
                part_dict = next((item for item in parts_keywords_times if item["part"] == part), None)
                if part_dict:
                    part_dict['keywords'] = keywords
                    # Also add the videos for these keywords
                    part_dict['videos'] = get_videos_for_keywords(keywords, pexels_api_key, pixabay_api_key)
                else:  # This is a new part, add it to the list
                    part_dict = {"part": part, "keywords": keywords, "start_time": 0,
                                 "end_time": 0, "videos": get_videos_for_keywords(keywords, pexels_api_key, pixabay_api_key)}
                    parts_keywords_times.append(part_dict)

            f.seek(0)  # Move the cursor to the beginning of the file
            json.dump(parts_keywords_times, f)
            f.truncate()  # Remove any leftover content

        logger.write('Keywords sauvegardés.', 'info')
        return redirect('video_selection')  # Redirect to the video selection view
