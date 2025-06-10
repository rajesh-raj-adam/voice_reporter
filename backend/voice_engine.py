import os
import torch
import soundfile as sf
import sounddevice as sd
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
from transformers import VitsModel, AutoTokenizer
import numpy as np
from typing import Optional

class VoiceEngine:
    def __init__(self):
        # Initialize speech-to-text model
        self.stt_model_name = "facebook/wav2vec2-base-960h"
        self.stt_processor = Wav2Vec2Processor.from_pretrained(self.stt_model_name)
        self.stt_model = Wav2Vec2ForCTC.from_pretrained(self.stt_model_name)
        
        # Initialize text-to-speech model
        self.tts_model_name = "facebook/mms-tts-eng"
        self.tts_tokenizer = AutoTokenizer.from_pretrained(self.tts_model_name)
        self.tts_model = VitsModel.from_pretrained(self.tts_model_name)
        
        # Move models to GPU if available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.stt_model.to(self.device)
        self.tts_model.to(self.device)
        
        # Create output directory for audio files
        os.makedirs("audio_output", exist_ok=True)

    def speech_to_text(self, audio_file_path: str) -> str:
        """Convert speech to text using Wav2Vec2."""
        # Load audio file
        audio_input, sample_rate = sf.read(audio_file_path)
        
        # Process audio input
        inputs = self.stt_processor(
            audio_input, 
            sampling_rate=sample_rate, 
            return_tensors="pt", 
            padding=True
        )
        
        # Move inputs to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Perform inference
        with torch.no_grad():
            logits = self.stt_model(**inputs).logits
        
        # Decode the output
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = self.stt_processor.batch_decode(predicted_ids)
        
        return transcription[0]

    def text_to_speech(self, text: str, output_file: Optional[str] = None) -> str:
        """Convert text to speech using VITS model."""
        # Tokenize text
        inputs = self.tts_tokenizer(text, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Generate speech
        with torch.no_grad():
            output = self.tts_model(**inputs).waveform
        
        # Convert to numpy array
        audio = output.cpu().numpy().squeeze()
        
        # Generate output filename if not provided
        if output_file is None:
            output_file = f"audio_output/tts_{hash(text)}.wav"
        
        # Save audio file
        sf.write(output_file, audio, self.tts_model.config.sampling_rate)
        
        return output_file

    def record_audio(self, duration: int = 5, sample_rate: int = 16000) -> str:
        """Record audio from microphone."""
        print(f"Recording for {duration} seconds...")
        
        # Record audio
        recording = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype='float32'
        )
        sd.wait()
        
        # Generate output filename
        output_file = f"audio_output/recording_{hash(str(recording))}.wav"
        
        # Save recording
        sf.write(output_file, recording, sample_rate)
        
        return output_file

    def play_audio(self, audio_file_path: str):
        """Play audio file."""
        # Load audio file
        audio_data, sample_rate = sf.read(audio_file_path)
        
        # Play audio
        sd.play(audio_data, sample_rate)
        sd.wait() 