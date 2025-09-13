import React, { useState } from 'react';
import {
  TextField,
  Button,
  Box,
  Paper,
  Typography,
  CircularProgress,
  Chip
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';

interface Props {
  onQuery: (query: string) => void;
  loading: boolean;
}

const QueryInput: React.FC<Props> = ({ onQuery, loading }) => {
  const [query, setQuery] = useState('');

  const sampleQueries = [
    "show me temperature average for each profile",
    "highest temperature readings",
    "floats in southern ocean", 
    "salinity data by depth",
    "temperature distribution"
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !loading) {
      onQuery(query.trim());
    }
  };

  const handleSampleQuery = (sampleQuery: string) => {
    setQuery(sampleQuery);
    onQuery(sampleQuery);
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Natural Language Query
      </Typography>
      
      <Box component="form" onSubmit={handleSubmit} sx={{ mb: 2 }}>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Ask about oceanographic data (e.g., 'show temperature for each profile')"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={loading}
            size="medium"
          />
          <Button
            type="submit"
            variant="contained"
            disabled={loading || !query.trim()}
            sx={{ minWidth: '120px' }}
          >
            {loading ? (
              <CircularProgress size={24} color="inherit" />
            ) : (
              <>
                <SearchIcon sx={{ mr: 1 }} />
                Query
              </>
            )}
          </Button>
        </Box>
      </Box>

      <Box>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Try these sample queries:
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {sampleQueries.map((sample, index) => (
            <Chip
              key={index}
              label={sample}
              onClick={() => handleSampleQuery(sample)}
              variant="outlined"
              size="small"
              disabled={loading}
              sx={{ cursor: 'pointer' }}
            />
          ))}
        </Box>
      </Box>
    </Paper>
  );
};

export default QueryInput;