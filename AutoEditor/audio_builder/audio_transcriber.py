import pvleopard
from pydub import AudioSegment

class Audio:
    def __init__(self, file_path):
        self.file_path = file_path
        self.transcriptions = []

    def convert_to_wav(self):
        # Check if the file is already in WAV format
        if self.file_path.lower().endswith('.wav'):
            return

        # Load the MP3 audio file
        audio = AudioSegment.from_file(self.file_path, format='mp3')

        # Change the file extension to WAV
        wav_file_path = self.file_path.rsplit('.', 1)[0] + '.wav'

        # Export the audio in WAV format
        audio.export(wav_file_path, format='wav')

        # Update the file path to the converted WAV file
        self.file_path = wav_file_path

    def convert_m4a_to_mp3(self):
        # Check if the file is in m4a format
        if not self.file_path.lower().endswith('.m4a'):
            print("File is not in .m4a format")
            return

        # Load the m4a audio file
        audio = AudioSegment.from_file(self.file_path, format='m4a')

        # Change the file extension to mp3
        mp3_file_path = self.file_path.rsplit('.', 1)[0] + '.mp3'

        # Export the audio in mp3 format
        audio.export(mp3_file_path, format='mp3')

        # Update the file path to the converted mp3 file
        self.file_path = mp3_file_path

    def transcribe(self):
        leopard = pvleopard.create(access_key="JHRxxr3akK4RilsSIOyULG8IMwwmbMQX6fLcTeB2yXgXSsDWcexbdA==",
                                   model_path="/Users/evanflament/Documents/Git-Projects/"
                                              "AutoEditor/AutoEditor/leopard_params_fr.pv")

        # Process the audio file
        transcript, words = leopard.process_file(self.file_path)

        # Convert the words to transcriptions format
        for i, word in enumerate(words):
            pause_after = words[i + 1].start_sec - word.end_sec if i + 1 < len(words) else 0
            self.transcriptions.append({
                'word': word.word,
                'start_time': word.start_sec,
                'end_time': word.end_sec,
                'confidence': word.confidence,
                'pause_after': pause_after
            })

    @property
    def get_transcriptions(self):
        return self.transcriptions
