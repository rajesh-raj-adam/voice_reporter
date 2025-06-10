import React, { useState } from 'react';
import { 
  Container, 
  Box, 
  Typography, 
  Paper,
  ThemeProvider,
  createTheme
} from '@mui/material';
import DocumentUpload from './components/DocumentUpload';
import VoiceInterface from './components/VoiceInterface';
import ResponseDisplay from './components/ResponseDisplay';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  const [currentDocument, setCurrentDocument] = useState(null);
  const [responses, setResponses] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleError = (error, context) => {
    let errorMessage = 'An unexpected error occurred';
    
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      const data = error.response.data;
      errorMessage = data.detail || data.message || `Error: ${error.response.status}`;
    } else if (error.request) {
      // The request was made but no response was received
      errorMessage = 'No response from server. Please check if the backend is running.';
    } else {
      // Something happened in setting up the request that triggered an Error
      errorMessage = error.message;
    }
    
    setResponses(prev => [...prev, {
      type: 'error',
      content: `${context}: ${errorMessage}`,
    }]);
  };

  const handleDocumentUpload = async (file) => {
    setIsProcessing(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to upload document');
      }

      const data = await response.json();
      setCurrentDocument({
        id: data.document_id,
        name: file.name,
      });
      setResponses([{
        type: 'system',
        content: 'Document uploaded successfully. You can now ask questions about it.',
      }]);
    } catch (error) {
      handleError(error, 'Error uploading document');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleQuery = async (query) => {
    if (!currentDocument) {
      setResponses([{
        type: 'error',
        content: 'Please upload a document first.',
      }]);
      return;
    }

    setIsProcessing(true);
    try {
      setResponses(prev => [...prev, { type: 'user', content: query }]);

      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: query,
          document_id: currentDocument.id,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to process query');
      }

      const data = await response.json();
      
      setResponses(prev => [
        ...prev,
        {
          type: data.type || 'assistant',
          content: data.response,
          audioUrl: data.audio_url,
          context: data.context
        }
      ]);
    } catch (error) {
      handleError(error, 'Error processing query');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <Container maxWidth="md">
        <Box sx={{ my: 4 }}>
          <Typography variant="h3" component="h1" gutterBottom align="center">
            Document Analysis Agent
          </Typography>
          
          <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
            <DocumentUpload 
              onUpload={handleDocumentUpload}
              isProcessing={isProcessing}
            />
          </Paper>

          {currentDocument && (
            <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
              <Typography variant="subtitle1" gutterBottom>
                Current Document: {currentDocument.name}
              </Typography>
            </Paper>
          )}

          <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
            <VoiceInterface 
              onQuery={handleQuery}
              isProcessing={isProcessing}
            />
          </Paper>

          <Paper elevation={3} sx={{ p: 3 }}>
            <ResponseDisplay responses={responses} />
          </Paper>
        </Box>
      </Container>
    </ThemeProvider>
  );
}

export default App; 