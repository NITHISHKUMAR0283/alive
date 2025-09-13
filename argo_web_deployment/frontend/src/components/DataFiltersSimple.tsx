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

const DataFiltersSimple: React.FC<Props> = ({ onFiltersChange, availableData }) => {
  const [filters, setFilters] = useState<FilterOptions>({
    timeRange: {
      startDate: '',
      endDate: ''
    },
    geographicalArea: {
      latRange: [availableData.geoRange.latMin, availableData.geoRange.latMax],
      lonRange: [availableData.geoRange.lonMin, availableData.geoRange.lonMax]
    },
    depthRange: [availableData.depthRange.min, availableData.depthRange.max],
    dataParameters: availableData.parameters,
    deploymentYear: [2000, new Date().getFullYear()],
    dataQuality: ['1', '2'],
    networkType: []
  });

  const [activeFiltersCount, setActiveFiltersCount] = useState(0);

  useEffect(() => {
    // Count active filters
    let count = 0;
    if (filters.timeRange.startDate || filters.timeRange.endDate) count++;
    if (filters.geographicalArea.latRange[0] !== availableData.geoRange.latMin || 
        filters.geographicalArea.latRange[1] !== availableData.geoRange.latMax) count++;
    if (filters.geographicalArea.lonRange[0] !== availableData.geoRange.lonMin || 
        filters.geographicalArea.lonRange[1] !== availableData.geoRange.lonMax) count++;
    if (filters.depthRange[0] !== availableData.depthRange.min || 
        filters.depthRange[1] !== availableData.depthRange.max) count++;
    if (filters.dataParameters.length !== availableData.parameters.length) count++;
    if (filters.dataQuality.length > 0) count++;
    if (filters.networkType.length > 0) count++;
    
    setActiveFiltersCount(count);
    onFiltersChange(filters);
  }, [filters, onFiltersChange, availableData]);

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
        latRange: [availableData.geoRange.latMin, availableData.geoRange.latMax],
        lonRange: [availableData.geoRange.lonMin, availableData.geoRange.lonMax]
      },
      depthRange: [availableData.depthRange.min, availableData.depthRange.max],
      dataParameters: availableData.parameters,
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
                min={availableData.geoRange.latMin}
                max={availableData.geoRange.latMax}
                step={0.1}
                marks={[
                  { value: availableData.geoRange.latMin, label: `${availableData.geoRange.latMin}°` },
                  { value: availableData.geoRange.latMax, label: `${availableData.geoRange.latMax}°` }
                ]}
              />
            </Box>
            <Box>
              <Typography gutterBottom>Longitude Range</Typography>
              <Slider
                value={filters.geographicalArea.lonRange}
                onChange={(_, value) => handleGeographicalChange('lonRange', value as [number, number])}
                valueLabelDisplay="auto"
                min={availableData.geoRange.lonMin}
                max={availableData.geoRange.lonMax}
                step={0.1}
                marks={[
                  { value: availableData.geoRange.lonMin, label: `${availableData.geoRange.lonMin}°` },
                  { value: availableData.geoRange.lonMax, label: `${availableData.geoRange.lonMax}°` }
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
              min={availableData.depthRange.min}
              max={availableData.depthRange.max}
              step={10}
              marks={[
                { value: availableData.depthRange.min, label: `${availableData.depthRange.min}m` },
                { value: availableData.depthRange.max, label: `${availableData.depthRange.max}m` }
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
            {availableData.parameters.map((parameter) => (
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
              {availableData.qualityLevels.map((level) => (
                <MenuItem key={level} value={level}>
                  Level {level}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </AccordionDetails>
      </Accordion>
    </Paper>
  );
};

export default DataFiltersSimple;