from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from threading import Thread
from AutoEditor.Brain.brain import Helper
from AutoEditor.Logger.logger import Logger
import json
from django.http import HttpResponse, JsonResponse
import os

logger = Logger('AutoEditor.log')


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
    if request.method == 'POST':
        # Retrieve selected keywords from session
        selected_keywords = request.session.get('selected_keywords')

        # Retrieve videos matching the selected keywords
        # (For now, we will assume that you have a function 'get_videos_for_keywords'
        # that returns a list of video URLs for a given list of keywords.)
        videos = get_videos_for_keywords(selected_keywords)

        return render(request, 'video_selection.html', {'videos': videos})

    return redirect('index')  # Redirect to index if not POST


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
    # Check if the JSON file exists and delete it before processing
    if os.path.isfile('parts_keywords_times.json'):
        os.remove('parts_keywords_times.json')
        logger.write('Ancien fichier JSON supprimé.', 'info')

    options = {
        "audio_path": audio_path,
        "script_path": script_path
    }
    logger.write('Début de la génération des Keywords...', 'info')
    parts_keywords_times = Helper(options, logger)
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
        return render(request, 'keywords.html', {'parts_keywords_times': parts_keywords_times})
    except FileNotFoundError:
        logger.write('Le fichier JSON n\'a pas été trouvé, rediriger vers index.', 'info')
        return redirect('index')


def save_keywords(request):
    logger.write('Sauvegarder les keywords.', 'info')
    if request.method == 'POST':
        selected_keywords = {}
        for part in request.POST.keys():
            if part != "csrfmiddlewaretoken":  # Ignore the csrf token
                selected_keywords[part] = request.POST.getlist(part)  # Get the selected keywords for this part

        # Update the JSON file with the new selected keywords
        with open('parts_keywords_times.json', 'r+') as f:
            parts_keywords_times = json.load(f)

            for part, keywords in selected_keywords.items():
                for part_dict in parts_keywords_times:
                    if part_dict['part'] == part:
                        part_dict['keywords'] = keywords
                        # Also add the videos for these keywords
                        part_dict['videos'] = get_videos_for_keywords(keywords)

            f.seek(0)  # Move the cursor to the beginning of the file
            json.dump(parts_keywords_times, f)
            f.truncate()  # Remove any leftover content

        logger.write('Keywords sauvegardés.', 'info')
        return redirect('video_selection')  # Redirect to the video selection view


def get_videos_for_part(request, part_name):
    # Load the JSON file
    with open('parts_keywords_times.json', 'r') as f:
        parts_keywords_times = json.load(f)

    # Find the part with the given name
    for part in parts_keywords_times:
        if part['part'] == part_name:
            # Return the list of videos for this part
            return JsonResponse({'videos': part['videos']})

    # If no part was found with the given name, return an error
    return JsonResponse({'error': 'Part not found'}, status=404)
