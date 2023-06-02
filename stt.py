import io
import os
import wave
import json
import vosk
import config
import subprocess

from pydub import AudioSegment
from vosk import Model, KaldiRecognizer


class STT:
    """
    Class for recognizing audio through Vosk and converting it to text.
     Supported audio formats: wav, ogg
    """
    default_init = {
        "model_path": "model_small",  # path to the folder with STT files of the Vosk model
        "sample_rate": 16000,
        "ffmpeg_path": config.ffmpeg_path  # path to ffmpeg
    }

    def __init__(self,
                 model_path=None,
                 sample_rate=None,
                 ffmpeg_path=None
                 ) -> None:
        """
        Setting up the Vosk model for audio recognition and
         converting it to text.

        :arg model_path: str path to the Vosk model
        :arg sample_rate: int sample rate, typically 16000
        :arg ffmpeg_path: str path to ffmpeg
        """
        self.model_path = model_path if model_path else STT.default_init["model_path"]
        self.sample_rate = sample_rate if sample_rate else STT.default_init["sample_rate"]
        self.ffmpeg_path = ffmpeg_path if ffmpeg_path else STT.default_init["ffmpeg_path"]

        

        model = Model(self.model_path)
        self.recognizer = KaldiRecognizer(model, self.sample_rate)
        self.recognizer.SetWords(True)

    
    def audio_to_text(self, audio_file_name=None) -> str:
        """
        Offline audio to text recognition via Vosk
        :param audio_file_name: str path and name of the audio file
         :return: str recognized text
        """
        # Convert audio to wav and result in process.stdout
        process = subprocess.Popen(
            [self.ffmpeg_path,
             "-loglevel", "quiet",
             "-i", audio_file_name,          # input file name
             "-ar", str(self.sample_rate),   # sample rate
             "-ac", "1",                     # number of channels
             "-f", "s16le",                  # codec for transcoding, we have wav
             "-"                             # there is no output file name, because we read from stdout
             ],
            stdout=subprocess.PIPE
                                   )

        # Reading data in chunks and recognizing through the model
        while True:
            data = process.stdout.read(4000)
            if len(data) == 0:
                break
            if self.recognizer.AcceptWaveform(data):
                pass

        # Return the recognized text as a str
        result_json = self.recognizer.FinalResult()  # this is json as a str
        result_dict = json.loads(result_json)    # this is a dict
        return result_dict["text"]               # text as str



