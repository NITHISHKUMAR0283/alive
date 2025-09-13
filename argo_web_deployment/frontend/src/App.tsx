import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import OceanographicGlobe from './components/OceanographicGlobe';
import QueryInput from './components/QueryInput';
import DataTable from './components/DataTable';
import DataFilters from './components/DataFilters';
import { Container, Typography, Box, Paper } from '@mui/material';

interface FloatData {
  float_id: number;
  latitude: number;
  longitude: number;
  profiles_count: number;
  avg_temperature?: number;
  deployment_date?: string;
}

interface QueryResult {
  data: any[];
  pagination: {
    total_records: number;
    current_page: number;
    page_size: number;
    total_pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
  query_metadata: {
    intent: any;
    similarity: number;
    method: string;
    sql_preview?: string;
  };
}

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [floatData, setFloatData] = useState<FloatData[]>([]);
  const [queryResult, setQueryResult] = useState<QueryResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastQuery, setLastQuery] = useState<string>('');
  const [filterOptions, setFilterOptions] = useState({
    parameters: ['temperature', 'salinity', 'pressure'],
    qualityLevels: ['1', '2', '3', '4'],
    networks: ['ARGO', 'CORE-ARGO'],
    dateRange: { min: '2000-01-01', max: '2024-12-31' },
    depthRange: { min: 0, max: 2000 },
    geoRange: { latMin: -80, latMax: 80, lonMin: -180, lonMax: 180 }
  });

  // Load float data and filter options on component mount
  useEffect(() => {
    fetchFloatData();
    fetchFilterOptions();
  }, []);

  const fetchFloatData = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/floats-3d`);
      if (response.ok) {
        const data = await response.json();
        setFloatData(data.floats || []);
      } else {
        console.warn('Backend API not available, using empty float data');
        setFloatData([]);
      }
    } catch (err) {
      console.error('Failed to fetch float data:', err);
      setFloatData([]);
    }
  };

  const fetchFilterOptions = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/filter-options`);
      if (response.ok) {
        const data = await response.json();
        setFilterOptions(data);
      } else {
        console.warn('Failed to fetch filter options, using defaults');
      }
    } catch (err) {
      console.error('Failed to fetch filter options:', err);
      // Keep using the default values already set in state
    }
  };

  const handleQuery = async (query: string, page: number = 1) => {
    setLoading(true);
    setError(null);
    setLastQuery(query);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/query?page=${page}&page_size=100`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setQueryResult(result);
    } catch (err) {
      console.error('Query failed:', err);
      setError('Query failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (page: number) => {
    if (lastQuery) {
      handleQuery(lastQuery, page);
    }
  };

  const handleFiltersChange = useCallback(async (filters: any) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/filtered-data?page=1&page_size=100`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(filters),
      });

      if (!response.ok) {
        if (response.status === 404) {
          console.warn('Backend API not available, skipping filter query');
          return;
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setQueryResult(result);
    } catch (err) {
      console.error('Filter query failed:', err);
      setError('Filter query failed. Please try again.');
    } finally {
      setLoading(false);
    }
  }, []);

  return (
    <div className="App">
      <Container maxWidth="xl">
        <Box sx={{ py: 2 }}>
          <Typography variant="h3" component="h1" gutterBottom align="center">
            ARGO Oceanographic 3D Explorer
          </Typography>
          
          <Typography variant="subtitle1" align="center" color="text.secondary" gutterBottom>
            Interactive 3D globe for oceanographic data exploration
          </Typography>

          {error && (
            <Paper sx={{ p: 2, mb: 2, bgcolor: 'error.light', color: 'error.contrastText' }}>
              {error}
            </Paper>
          )}

          <Box sx={{ mb: 3 }}>
            <QueryInput onQuery={handleQuery} loading={loading} />
          </Box>

          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            {/* Data Filters Sidebar */}
            <Box sx={{ flex: '0 0 300px', minWidth: '300px' }}>
              <Paper sx={{ height: '700px' }}>
                <DataFilters 
                  onFiltersChange={handleFiltersChange}
                  availableData={filterOptions}
                />
              </Paper>
            </Box>

            {/* 3D Globe */}
            <Box sx={{ flex: '1 1 600px', minWidth: '600px' }}>
              <Paper sx={{ p: 1, height: '700px' }}>
                <OceanographicGlobe 
                  floatData={floatData} 
                  queryResult={queryResult}
                />
              </Paper>
            </Box>

            {/* Data Table */}
            <Box sx={{ flex: '0 0 300px', minWidth: '300px' }}>
              <Paper sx={{ p: 2, height: '700px', overflow: 'auto' }}>
                <DataTable 
                  queryResult={queryResult}
                  onPageChange={handlePageChange}
                />
              </Paper>
            </Box>
          </Box>

          {floatData.length > 0 && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" color="text.secondary" align="center">
                Loaded {floatData.length} ARGO floats • 
                Total profiles: {floatData.reduce((sum, f) => sum + f.profiles_count, 0).toLocaleString()}
              </Typography>
            </Box>
          )}
        </Box>
      </Container>
    </div>
  );
}

export default App;