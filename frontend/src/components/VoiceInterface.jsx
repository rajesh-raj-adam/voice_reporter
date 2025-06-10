import React, { useState, useEffect } from 'react';
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
import {
  Box,
  TextField,
  IconButton,
  Typography,
  CircularProgress,
  Paper
} from '@mui/material';
import MicIcon from '@mui/icons-material/Mic';
import MicOffIcon from '@mui/icons-material/MicOff';
import SendIcon from '@mui/icons-material/Send';

const VoiceInterface = ({ onQuery, isProcessing }) => {
  const [query, setQuery] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [audioElement, setAudioElement] = useState(null);

  const {
    transcript,
    listening,
    resetTranscript,
    browserSupportsSpeechRecognition
  } = useSpeechRecognition();

  useEffect(() => {
    if (transcript) {
      setQuery(transcript);
    }
  }, [transcript]);

  const handleStartListening = () => {
    setIsListening(true);
    SpeechRecognition.startListening({ continuous: true });
  };

  const handleStopListening = () => {
    setIsListening(false);
    SpeechRecognition.stopListening();
  };

  const handleSubmit = async () => {
    if (query.trim()) {
      await onQuery(query);
      setQuery('');
      resetTranscript();
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSubmit();
    }
  };

  const playAudio = (audioUrl) => {
    if (audioElement) {
      audioElement.pause();
    }
    const audio = new Audio(audioUrl);
    setAudioElement(audio);
    audio.play();
  };

  if (!browserSupportsSpeechRecognition) {
    return (
      <Box>
        <Typography color="error">
          Your browser doesn't support speech recognition. Please use a modern browser.
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Ask Questions
      </Typography>

      <Paper
        sx={{
          p: 2,
          display: 'flex',
          alignItems: 'center',
          gap: 1
        }}
      >
        <TextField
          fullWidth
          multiline
          maxRows={4}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your question or click the microphone to speak..."
          disabled={isProcessing}
          InputProps={{
            endAdornment: (
              <Box sx={{ display: 'flex', gap: 1 }}>
                <IconButton
                  onClick={isListening ? handleStopListening : handleStartListening}
                  color={isListening ? 'secondary' : 'primary'}
                >
                  {isListening ? <MicOffIcon /> : <MicIcon />}
                </IconButton>
                <IconButton
                  onClick={handleSubmit}
                  disabled={!query.trim() || isProcessing}
                  color="primary"
                >
                  {isProcessing ? <CircularProgress size={24} /> : <SendIcon />}
                </IconButton>
              </Box>
            ),
          }}
        />
      </Paper>

      {isListening && (
        <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
          Listening... {transcript}
        </Typography>
      )}
    </Box>
  );
};

export default VoiceInterface; 