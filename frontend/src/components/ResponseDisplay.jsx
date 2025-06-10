import React from 'react';
import {
  Box,
  Typography,
  Paper,
  IconButton,
  Divider
} from '@mui/material';
import VolumeUpIcon from '@mui/icons-material/VolumeUp';
import ErrorIcon from '@mui/icons-material/Error';
import InfoIcon from '@mui/icons-material/Info';

const ResponseDisplay = ({ responses }) => {
  const playAudio = (audioUrl) => {
    const audio = new Audio(audioUrl);
    audio.play();
  };

  const getMessageStyle = (type) => {
    switch (type) {
      case 'user':
        return {
          backgroundColor: 'primary.light',
          color: 'primary.contrastText',
          alignSelf: 'flex-end',
        };
      case 'assistant':
        return {
          backgroundColor: 'background.paper',
          border: '1px solid',
          borderColor: 'divider',
          alignSelf: 'flex-start',
        };
      case 'error':
        return {
          backgroundColor: 'error.light',
          color: 'error.contrastText',
          alignSelf: 'center',
        };
      case 'system':
        return {
          backgroundColor: 'info.light',
          color: 'info.contrastText',
          alignSelf: 'center',
        };
      default:
        return {};
    }
  };

  const getIcon = (type) => {
    switch (type) {
      case 'error':
        return <ErrorIcon />;
      case 'system':
        return <InfoIcon />;
      default:
        return null;
    }
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Conversation
      </Typography>

      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          gap: 2,
          maxHeight: '400px',
          overflowY: 'auto',
          p: 1,
        }}
      >
        {responses.map((response, index) => (
          <React.Fragment key={index}>
            <Paper
              elevation={1}
              sx={{
                p: 2,
                maxWidth: '80%',
                ...getMessageStyle(response.type),
                display: 'flex',
                alignItems: 'flex-start',
                gap: 1,
              }}
            >
              {getIcon(response.type)}
              <Box sx={{ flex: 1 }}>
                <Typography variant="body1">
                  {response.content}
                </Typography>
              </Box>
              {response.audioUrl && (
                <IconButton
                  size="small"
                  onClick={() => playAudio(response.audioUrl)}
                  sx={{ ml: 1 }}
                >
                  <VolumeUpIcon />
                </IconButton>
              )}
            </Paper>
            {index < responses.length - 1 && <Divider />}
          </React.Fragment>
        ))}
      </Box>
    </Box>
  );
};

export default ResponseDisplay; 