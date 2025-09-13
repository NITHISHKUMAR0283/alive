import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  Box,
  Pagination,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

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

interface Props {
  queryResult: QueryResult | null;
  onPageChange: (page: number) => void;
}

const DataTable: React.FC<Props> = ({ queryResult, onPageChange }) => {
  if (!queryResult) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <Typography variant="h6" color="text.secondary">
          No query results yet
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Enter a natural language query to see oceanographic data
        </Typography>
      </Box>
    );
  }

  const { data, pagination, query_metadata } = queryResult;

  const handlePageChange = (event: React.ChangeEvent<unknown>, value: number) => {
    onPageChange(value);
  };

  // Get column names from first row
  const columns = data.length > 0 ? Object.keys(data[0]) : [];

  const formatValue = (value: any): string => {
    if (value === null || value === undefined) return 'N/A';
    if (typeof value === 'number') {
      return Number.isInteger(value) ? value.toString() : value.toFixed(3);
    }
    return value.toString();
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Query Results
      </Typography>

      {/* Query Metadata */}
      <Accordion sx={{ mb: 2 }}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="subtitle2">Query Information</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <Box>
              <Chip 
                label={`Method: ${query_metadata.method}`} 
                size="small" 
                variant="outlined" 
              />
              <Chip 
                label={`Similarity: ${typeof query_metadata.similarity === 'number' ? query_metadata.similarity.toFixed(3) : 'N/A'}`} 
                size="small" 
                variant="outlined" 
                sx={{ ml: 1 }}
              />
            </Box>
            {query_metadata.intent && (
              <Typography variant="caption" color="text.secondary">
                Intent: {JSON.stringify(query_metadata.intent, null, 2)}
              </Typography>
            )}
            {query_metadata.sql_preview && (
              <Typography variant="caption" color="text.secondary" sx={{ fontFamily: 'monospace' }}>
                SQL: {query_metadata.sql_preview}
              </Typography>
            )}
          </Box>
        </AccordionDetails>
      </Accordion>

      {/* Data Table */}
      {data.length > 0 ? (
        <>
          <TableContainer component={Paper} sx={{ maxHeight: 400, mb: 2 }}>
            <Table stickyHeader size="small">
              <TableHead>
                <TableRow>
                  {columns.map((column) => (
                    <TableCell key={column} sx={{ fontWeight: 'bold' }}>
                      {column.replace(/_/g, ' ').toUpperCase()}
                    </TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {data.map((row, index) => (
                  <TableRow key={index} hover>
                    {columns.map((column) => (
                      <TableCell key={column}>
                        {formatValue(row[column])}
                      </TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          {/* Pagination */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              Showing {((pagination.current_page - 1) * pagination.page_size) + 1} - {Math.min(pagination.current_page * pagination.page_size, pagination.total_records)} of {pagination.total_records.toLocaleString()} records
            </Typography>
            
            <Pagination
              count={pagination.total_pages}
              page={pagination.current_page}
              onChange={handlePageChange}
              showFirstButton
              showLastButton
              size="small"
            />
          </Box>
        </>
      ) : (
        <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
          No data found for this query
        </Typography>
      )}
    </Box>
  );
};

export default DataTable;