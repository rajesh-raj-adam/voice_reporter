import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { 
  Box, 
  Typography, 
  CircularProgress,
  Paper
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

const DocumentUpload = ({ onUpload, isProcessing }) => {
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      onUpload(acceptedFiles[0]);
    }
  }, [onUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'text/plain': ['.txt'],
      'image/*': ['.png', '.jpg', '.jpeg']
    },
    multiple: false
  });

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Upload Document
      </Typography>
      
      <Paper
        {...getRootProps()}
        sx={{
          p: 3,
          textAlign: 'center',
          cursor: 'pointer',
          backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'divider',
          '&:hover': {
            backgroundColor: 'action.hover',
          },
        }}
      >
        <input {...getInputProps()} />
        
        {isProcessing ? (
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <CircularProgress size={40} />
            <Typography sx={{ mt: 2 }}>
              Processing document...
            </Typography>
          </Box>
        ) : (
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
            <Typography>
              {isDragActive
                ? 'Drop the file here'
                : 'Drag and drop a file here, or click to select a file'}
            </Typography>
            <Typography variant="caption" color="textSecondary" sx={{ mt: 1 }}>
              Supported formats: PDF, DOCX, XLSX, TXT, PNG, JPG
            </Typography>
          </Box>
        )}
      </Paper>
    </Box>
  );
};

export default DocumentUpload; 