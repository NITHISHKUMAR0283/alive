import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Slider,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  TextField,
  Chip,
  Stack
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import FilterListIcon from '@mui/icons-material/FilterList';
import ClearIcon from '@mui/icons-material/Clear';

interface FilterOptions {
  timeRange: {
    startDate: string;
    endDate: string;
  };
  geographicalArea: {
    latRange: [number, number];
    lonRange: [number, number];
  };
  depthRange: [number, number];
  dataParameters: string[];
  deploymentYear: [number, number];
  dataQuality: string[];
  networkType: string[];
}

interface Props {
  onFiltersChange: (filters: FilterOptions) => void;
  availableData: {
    parameters: string[];
    qualityLevels: string[];
    networks: string[];
    dateRange: { min: string; max: string };
    depthRange: { min: number; max: number };
    geoRange: { latMin: number; latMax: number; lonMin: number; lonMax: number };
  };
}

const DataFilters: React.FC<Props> = ({ onFiltersChange, availableData }) => {
  // Default values to prevent undefined errors
  const defaultGeoRange = { latMin: -80, latMax: 80, lonMin: -180, lonMax: 180 };
  const defaultDepthRange = { min: 0, max: 2000 };
  const defaultParameters = ['temperature', 'salinity', 'pressure'];
  const defaultQualityLevels = ['1', '2', '3', '4'];
  const defaultNetworks = ['ARGO', 'CORE-ARGO'];
  const defaultDateRange = { min: '2000-01-01', max: '2024-12-31' };

  const safeAvailableData = availableData || {
    parameters: defaultParameters,
    qualityLevels: defaultQualityLevels,
    networks: defaultNetworks,
    dateRange: defaultDateRange,
    depthRange: defaultDepthRange,
    geoRange: defaultGeoRange
  };

  const [filters, setFilters] = useState<FilterOptions>({
    timeRange: {
      startDate: '',
      endDate: ''
    },
    geographicalArea: {
      latRange: [safeAvailableData.geoRange.latMin, safeAvailableData.geoRange.latMax],
      lonRange: [safeAvailableData.geoRange.lonMin, safeAvailableData.geoRange.lonMax]
    },
    depthRange: [safeAvailableData.depthRange.min, safeAvailableData.depthRange.max],
    dataParameters: safeAvailableData.parameters,
    deploymentYear: [2000, new Date().getFullYear()],
    dataQuality: ['good'],
    networkType: []
  });

  const [activeFiltersCount, setActiveFiltersCount] = useState(0);
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    // Count active filters
    let count = 0;
    if (filters.timeRange.startDate || filters.timeRange.endDate) count++;
    if (filters.geographicalArea.latRange[0] !== safeAvailableData.geoRange.latMin || 
        filters.geographicalArea.latRange[1] !== safeAvailableData.geoRange.latMax) count++;
    if (filters.geographicalArea.lonRange[0] !== safeAvailableData.geoRange.lonMin || 
        filters.geographicalArea.lonRange[1] !== safeAvailableData.geoRange.lonMax) count++;
    if (filters.depthRange[0] !== safeAvailableData.depthRange.min || 
        filters.depthRange[1] !== safeAvailableData.depthRange.max) count++;
    if (filters.dataParameters.length !== safeAvailableData.parameters.length) count++;
    if (filters.dataQuality.length > 0) count++;
    if (filters.networkType.length > 0) count++;
    
    setActiveFiltersCount(count);
    
    // Only call onFiltersChange after initialization and if there are active filters
    if (isInitialized && count > 0) {
      onFiltersChange(filters);
    }
    
    // Mark as initialized after first render
    if (!isInitialized) {
      setIsInitialized(true);
    }
  }, [filters, onFiltersChange, safeAvailableData, isInitialized]);

  const handleTimeRangeChange = (field: 'startDate' | 'endDate', value: string) => {
    setFilters(prev => ({
      ...prev,
      timeRange: {
        ...prev.timeRange,
        [field]: value
      }
    }));
  };

  const handleGeographicalChange = (field: 'latRange' | 'lonRange', value: [number, number]) => {
    setFilters(prev => ({
      ...prev,
      geographicalArea: {
        ...prev.geographicalArea,
        [field]: value
      }
    }));
  };

  const handleDepthRangeChange = (value: number | number[]) => {
    setFilters(prev => ({
      ...prev,
      depthRange: value as [number, number]
    }));
  };

  const handleParameterChange = (parameter: string, checked: boolean) => {
    setFilters(prev => ({
      ...prev,
      dataParameters: checked 
        ? [...prev.dataParameters, parameter]
        : prev.dataParameters.filter(p => p !== parameter)
    }));
  };

  const handleMultiSelectChange = (field: 'dataQuality' | 'networkType', value: string[]) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleDeploymentYearChange = (value: number | number[]) => {
    setFilters(prev => ({
      ...prev,
      deploymentYear: value as [number, number]
    }));
  };

  const resetFilters = () => {
    setFilters({
      timeRange: {
        startDate: '',
        endDate: ''
      },
      geographicalArea: {
        latRange: [safeAvailableData.geoRange.latMin, safeAvailableData.geoRange.latMax],
        lonRange: [safeAvailableData.geoRange.lonMin, safeAvailableData.geoRange.lonMax]
      },
      depthRange: [safeAvailableData.depthRange.min, safeAvailableData.depthRange.max],
      dataParameters: safeAvailableData.parameters,
      deploymentYear: [2000, new Date().getFullYear()],
      dataQuality: [],
      networkType: []
    });
  };

  return (
    <Paper sx={{ p: 2, height: '100%', overflow: 'auto' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <FilterListIcon sx={{ mr: 1 }} />
        <Typography variant="h6">
          Data Filters
        </Typography>
        {activeFiltersCount > 0 && (
          <Chip 
            size="small" 
            label={`${activeFiltersCount} active`} 
            color="primary" 
            sx={{ ml: 1 }}
          />
        )}
      </Box>

      <Button
        variant="outlined"
        startIcon={<ClearIcon />}
        onClick={resetFilters}
        fullWidth
        sx={{ mb: 2 }}
        disabled={activeFiltersCount === 0}
      >
        Reset All Filters
      </Button>

      {/* Time Period Selection */}
      <Accordion defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="subtitle1">Time Period</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Stack spacing={2}>
            <TextField
              label="Start Date"
              type="date"
              value={filters.timeRange.startDate}
              onChange={(e) => handleTimeRangeChange('startDate', e.target.value)}
              size="small"
              InputLabelProps={{ shrink: true }}
            />
            <TextField
              label="End Date"
              type="date"
              value={filters.timeRange.endDate}
              onChange={(e) => handleTimeRangeChange('endDate', e.target.value)}
              size="small"
              InputLabelProps={{ shrink: true }}
            />
          </Stack>
        </AccordionDetails>
      </Accordion>

        {/* Geographical Area */}
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="subtitle1">Geographical Area</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Stack spacing={3}>
              <Box>
                <Typography gutterBottom>Latitude Range</Typography>
                <Slider
                  value={filters.geographicalArea.latRange}
                  onChange={(_, value) => handleGeographicalChange('latRange', value as [number, number])}
                  valueLabelDisplay="auto"
                  min={safeAvailableData.geoRange.latMin}
                  max={safeAvailableData.geoRange.latMax}
                  step={0.1}
                  marks={[
                    { value: safeAvailableData.geoRange.latMin, label: `${safeAvailableData.geoRange.latMin}°` },
                    { value: safeAvailableData.geoRange.latMax, label: `${safeAvailableData.geoRange.latMax}°` }
                  ]}
                />
              </Box>
              <Box>
                <Typography gutterBottom>Longitude Range</Typography>
                <Slider
                  value={filters.geographicalArea.lonRange}
                  onChange={(_, value) => handleGeographicalChange('lonRange', value as [number, number])}
                  valueLabelDisplay="auto"
                  min={safeAvailableData.geoRange.lonMin}
                  max={safeAvailableData.geoRange.lonMax}
                  step={0.1}
                  marks={[
                    { value: safeAvailableData.geoRange.lonMin, label: `${safeAvailableData.geoRange.lonMin}°` },
                    { value: safeAvailableData.geoRange.lonMax, label: `${safeAvailableData.geoRange.lonMax}°` }
                  ]}
                />
              </Box>
            </Stack>
          </AccordionDetails>
        </Accordion>

        {/* Depth Range */}
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="subtitle1">Depth Range</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Box>
              <Typography gutterBottom>Depth (meters)</Typography>
              <Slider
                value={filters.depthRange}
                onChange={(_, value) => handleDepthRangeChange(value)}
                valueLabelDisplay="auto"
                min={safeAvailableData.depthRange.min}
                max={safeAvailableData.depthRange.max}
                step={10}
                marks={[
                  { value: safeAvailableData.depthRange.min, label: `${safeAvailableData.depthRange.min}m` },
                  { value: safeAvailableData.depthRange.max, label: `${safeAvailableData.depthRange.max}m` }
                ]}
              />
            </Box>
          </AccordionDetails>
        </Accordion>

        {/* Data Parameters */}
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="subtitle1">Data Parameters</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <FormGroup>
              {safeAvailableData.parameters.map((parameter) => (
                <FormControlLabel
                  key={parameter}
                  control={
                    <Checkbox
                      checked={filters.dataParameters.includes(parameter)}
                      onChange={(e) => handleParameterChange(parameter, e.target.checked)}
                      size="small"
                    />
                  }
                  label={parameter.charAt(0).toUpperCase() + parameter.slice(1)}
                />
              ))}
            </FormGroup>
          </AccordionDetails>
        </Accordion>

        {/* Deployment Year */}
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="subtitle1">Deployment Year</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Box>
              <Typography gutterBottom>Year Range</Typography>
              <Slider
                value={filters.deploymentYear}
                onChange={(_, value) => handleDeploymentYearChange(value)}
                valueLabelDisplay="auto"
                min={2000}
                max={new Date().getFullYear()}
                step={1}
                marks={[
                  { value: 2000, label: '2000' },
                  { value: new Date().getFullYear(), label: new Date().getFullYear().toString() }
                ]}
              />
            </Box>
          </AccordionDetails>
        </Accordion>

        {/* Data Quality */}
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="subtitle1">Data Quality</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <FormControl fullWidth size="small">
              <InputLabel>Quality Levels</InputLabel>
              <Select
                multiple
                value={filters.dataQuality}
                onChange={(e) => handleMultiSelectChange('dataQuality', e.target.value as string[])}
                renderValue={(selected) => (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {selected.map((value) => (
                      <Chip key={value} label={value} size="small" />
                    ))}
                  </Box>
                )}
              >
                {safeAvailableData.qualityLevels.map((level) => (
                  <MenuItem key={level} value={level}>
                    {level}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </AccordionDetails>
        </Accordion>

        {/* Network Type */}
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="subtitle1">Network Type</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <FormControl fullWidth size="small">
              <InputLabel>Network Types</InputLabel>
              <Select
                multiple
                value={filters.networkType}
                onChange={(e) => handleMultiSelectChange('networkType', e.target.value as string[])}
                renderValue={(selected) => (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {selected.map((value) => (
                      <Chip key={value} label={value} size="small" />
                    ))}
                  </Box>
                )}
              >
                {safeAvailableData.networks.map((network) => (
                  <MenuItem key={network} value={network}>
                    {network}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </AccordionDetails>
        </Accordion>
    </Paper>
  );
};

export default DataFilters;