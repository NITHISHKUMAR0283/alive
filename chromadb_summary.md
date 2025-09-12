# ARGO ChromaDB Knowledge Base Summary

## Collection Information
- **Name**: argo_comprehensive_knowledge
- **Total Documents**: 45
- **Knowledge Types**: 10

## Knowledge Type Breakdown

### Query Pattern (11 documents)

**Example 1:**
- ID: `query_warm_arabian_sea`
- Content: Query: "warm water Arabian Sea"
SQL Template: WITH region_profiles AS (
  SELECT profile_id FROM profiles WHERE latitude BETWEEN 10 AND 25 AND longitude BETWEEN 50 AND 75
)
SELECT p.profile_date, p.la...
- Metadata: {'domain': 'temperature', 'type': 'query_pattern', 'complexity': 'medium', 'region': 'arabian_sea'}

**Example 2:**
- ID: `query_salinity_arabian_sea`
- Content: Query: "salinity Arabian Sea"
SQL Template: WITH region_profiles AS (
  SELECT profile_id FROM profiles WHERE latitude BETWEEN 10 AND 25 AND longitude BETWEEN 50 AND 75
)
SELECT p.profile_date, p.lati...
- Metadata: {'domain': 'salinity', 'type': 'query_pattern', 'region': 'arabian_sea', 'complexity': 'medium'}

**Example 3:**
- ID: `query_warm_bay_of_bengal`
- Content: Query: "warm water Bay of Bengal"
SQL Template: WITH region_profiles AS (
  SELECT profile_id FROM profiles WHERE latitude BETWEEN 5 AND 25 AND longitude BETWEEN 80 AND 100
)
SELECT p.profile_date, p....
- Metadata: {'domain': 'temperature', 'region': 'bay_of_bengal', 'complexity': 'medium', 'type': 'query_pattern'}

... and 8 more documents

---

### Schema Info (5 documents)

**Example 1:**
- ID: `schema_floats`
- Content: Table: floats
Rows: 17
Columns: wmo_number (float ID), deployment_latitude, deployment_longitude, current_status
Purpose: Master registry of ARGO floats with deployment information
Key Usage: Float id...
- Metadata: {'row_count': 17, 'importance': 'high', 'type': 'schema_info', 'table': 'floats'}

**Example 2:**
- ID: `schema_profiles`
- Content: Table: profiles  
Rows: 3130
Columns: profile_id, float_id, profile_date, latitude, longitude, data_quality_flag
Purpose: Individual measurement cycles from floats
Key Usage: Spatial-temporal filterin...
- Metadata: {'row_count': 3130, 'table': 'profiles', 'importance': 'critical', 'type': 'schema_info'}

**Example 3:**
- ID: `schema_measurements`
- Content: Table: measurements
Rows: 1,425,648
Columns: profile_id, pressure, temperature, salinity, temperature_qc, salinity_qc
Purpose: Core oceanographic measurements
Key Usage: Temperature/salinity data extr...
- Metadata: {'row_count': 1425648, 'performance_warning': 'profile_first_required', 'type': 'schema_info', 'table': 'measurements', 'importance': 'critical'}

... and 2 more documents

---

### Domain Knowledge (5 documents)

**Example 1:**
- ID: `domain_arabian_sea`
- Content: Arabian Sea Characteristics:
Temperature: Summer surface temps 28-32°C, deep water <10°C below 1000m
Salinity: High salinity >36 PSU due to evaporation, low precipitation
Seasonality: Southwest monsoo...
- Metadata: {'parameters': 'temperature,salinity', 'type': 'domain_knowledge', 'region': 'arabian_sea', 'expertise': 'oceanography'}

**Example 2:**
- ID: `domain_bay_bengal`
- Content: Bay of Bengal Characteristics:  
Temperature: Similar to Arabian Sea but more variable, influenced by river discharge
Salinity: Lower salinity 28-34 PSU due to major rivers (Ganges, Brahmaputra)
Strat...
- Metadata: {'type': 'domain_knowledge', 'parameters': 'salinity,stratification', 'expertise': 'oceanography', 'region': 'bay_of_bengal'}

**Example 3:**
- ID: `domain_equatorial_indian`
- Content: Equatorial Indian Ocean:
Temperature: Warm year-round, 26-30°C at surface
Dynamics: Equatorial current system, seasonal reversals
Unique Features: Indian Ocean Dipole affects temperature patterns  
Va...
- Metadata: {'region': 'equatorial_indian_ocean', 'parameters': 'temperature,currents', 'type': 'domain_knowledge', 'expertise': 'oceanography'}

... and 2 more documents

---

### Sample Data (5 documents)

**Example 1:**
- ID: `sample_float_1`
- Content: Sample Float: WMO 2902746
Deployment Location: INDIAN-OCEAN-ARGO°N, UNKNOWN°E  
Current Status: argo-erddap
Context: This float represents typical ARGO deployment data
Usage: Reference this format whe...
- Metadata: {'subtype': 'float_example', 'type': 'sample_data', 'wmo_number': '2902746'}

**Example 2:**
- ID: `sample_float_2`
- Content: Sample Float: WMO 2902747
Deployment Location: INDIAN-OCEAN-ARGO°N, UNKNOWN°E  
Current Status: argo-erddap
Context: This float represents typical ARGO deployment data
Usage: Reference this format whe...
- Metadata: {'subtype': 'float_example', 'type': 'sample_data', 'wmo_number': '2902747'}

**Example 3:**
- ID: `sample_float_3`
- Content: Sample Float: WMO 2902748
Deployment Location: INDIAN-OCEAN-ARGO°N, UNKNOWN°E  
Current Status: argo-erddap
Context: This float represents typical ARGO deployment data
Usage: Reference this format whe...
- Metadata: {'subtype': 'float_example', 'type': 'sample_data', 'wmo_number': '2902748'}

... and 2 more documents

---

### Navigation Guide (4 documents)

**Example 1:**
- ID: `nav_float_queries`
- Content: Float Information Queries:
Question: "Show me all floats" / "Float list" / "Active floats"
-> Use: floats table
-> Join: LEFT JOIN profiles for counts/dates
-> Key columns: wmo_number, deployment_lati...
- Metadata: {'type': 'navigation_guide', 'query_category': 'float_information', 'table_primary': 'floats'}

**Example 2:**
- ID: `nav_measurement_queries`
- Content: Temperature/Salinity Data Queries:
Question: "Temperature in region" / "Warm water" / "Salinity profiles"
-> Use: measurements table (for data) + profiles table (for location/date)
-> CRITICAL: Always...
- Metadata: {'table_primary': 'measurements', 'query_category': 'oceanographic_data', 'type': 'navigation_guide', 'performance_critical': True}

**Example 3:**
- ID: `nav_spatial_queries`
- Content: Location-based Queries:
Question: "Data near location" / "Regional analysis"
-> Use: profiles table for spatial filtering
-> Geographic bounds: Arabian Sea (10-25°N, 50-75°E), Bay of Bengal (5-25°N, 8...
- Metadata: {'table_primary': 'profiles', 'query_category': 'spatial_queries', 'type': 'navigation_guide'}

... and 1 more documents

---

### Scientific Context (3 documents)

**Example 1:**
- ID: `context_qc_system`
- Content: ARGO Quality Control System:
QC Flag 1 (Good): Passed all automated tests, high confidence
QC Flag 2 (Probably Good): Minor issues detected, generally reliable  
QC Flag 3 (Probably Bad): Significant ...
- Metadata: {'importance': 'critical', 'topic': 'quality_control', 'type': 'scientific_context'}

**Example 2:**
- ID: `context_temp_salinity`
- Content: Temperature-Salinity Relationships:
Tropical Surface: High temperature (>28°C) + high salinity (>35 PSU) due to evaporation
River Influence: High temperature + low salinity (Bay of Bengal pattern)
Dee...
- Metadata: {'type': 'scientific_context', 'parameters': 'temperature,salinity', 'topic': 'parameter_relationships'}

**Example 3:**
- ID: `context_seasonal_patterns`
- Content: Indian Ocean Seasonal Patterns:
Southwest Monsoon (Jun-Sep): Cooling, mixing, upwelling
Northeast Monsoon (Dec-Mar): Calmer conditions, surface warming
Pre-monsoon (Apr-May): Highest temperatures, str...
- Metadata: {'type': 'scientific_context', 'topic': 'seasonal_variability', 'region': 'indian_ocean'}

---

### Error Solution (3 documents)

**Example 1:**
- ID: `solution_empty_results`
- Content: Empty Results Troubleshooting:
Problem: Query returns 0 rows
Possible Causes:
1. Region bounds too narrow -> Expand latitude/longitude ranges
2. Date range too restrictive -> Check data availability p...
- Metadata: {'problem': 'empty_results', 'type': 'error_solution', 'frequency': 'common'}

**Example 2:**
- ID: `solution_query_performance`
- Content: Query Performance Issues:
Problem: Query takes >10 seconds or times out
Cause: Full scan of measurements table (1.4M rows)
Solution: ALWAYS use profile-first filtering pattern:
1. WITH filtered_profil...
- Metadata: {'severity': 'critical', 'type': 'error_solution', 'problem': 'performance_timeout'}

**Example 3:**
- ID: `solution_unrealistic_values`
- Content: Unrealistic Data Values:
Problem: Temperature >50°C or <-10°C, Salinity >50 PSU or <0 PSU
Cause: Bad sensor data, not filtered by quality control
Solution: Always include quality control filters (temp...
- Metadata: {'solution_type': 'quality_filtering', 'problem': 'data_quality', 'type': 'error_solution'}

---

### Llm Instruction (3 documents)

**Example 1:**
- ID: `instruction_response_enhancement`
- Content: LLM Response Enhancement Guidelines:
1. Always mention data quality (QC flags used)
2. Provide oceanographic context for results
3. Explain spatial-temporal patterns observed  
4. Suggest related foll...
- Metadata: {'type': 'llm_instruction', 'purpose': 'response_enhancement', 'importance': 'high'}

**Example 2:**
- ID: `instruction_sql_enhancement`
- Content: SQL Query Enhancement by LLM:
1. Add quality control filters if missing
2. Include appropriate LIMIT clauses
3. Add date range filters for recent data focus
4. Optimize with profile-first filtering pa...
- Metadata: {'type': 'llm_instruction', 'importance': 'critical', 'purpose': 'sql_enhancement'}

**Example 3:**
- ID: `instruction_error_handling`
- Content: LLM Error Handling:
Empty Results: Explain possible causes, suggest alternative queries
Poor Performance: Mention optimization strategies
Data Quality Issues: Explain QC system, recommend filters
Regi...
- Metadata: {'purpose': 'error_handling', 'type': 'llm_instruction', 'importance': 'high'}

---

### Analytical Pattern (3 documents)

**Example 1:**
- ID: `pattern_regional_average`
- Content: Regional Average Analysis:
Pattern: Compare average temperature/salinity between regions
SQL Template: 
WITH region1 AS (SELECT AVG(temperature) as avg_temp FROM measurements m JOIN profiles p ON m.pr...
- Metadata: {'analysis_type': 'regional_comparison', 'type': 'analytical_pattern', 'complexity': 'medium'}

**Example 2:**
- ID: `pattern_time_series`
- Content: Time Series Analysis:
Pattern: Temperature/salinity trends over time
SQL Template:
SELECT DATE(profile_date) as date, AVG(temperature) as daily_avg_temp, COUNT(*) as measurements
FROM profiles p JOIN ...
- Metadata: {'type': 'analytical_pattern', 'complexity': 'medium', 'analysis_type': 'time_series'}

**Example 3:**
- ID: `pattern_depth_profile`
- Content: Vertical Profile Analysis:
Pattern: Temperature/salinity vs depth
SQL Template:
SELECT ROUND(pressure/50)*50 as depth_bin, AVG(temperature) as avg_temp, AVG(salinity) as avg_sal, COUNT(*) as measureme...
- Metadata: {'type': 'analytical_pattern', 'complexity': 'medium', 'analysis_type': 'vertical_profile'}

---

### External Context (3 documents)

**Example 1:**
- ID: `context_argo_overview`
- Content: ARGO Program Overview:
Global ocean observing system with ~4000 active floats worldwide
Established: 1999, operational since 2000
Coverage: Global oceans, real-time and delayed mode data
Mission: Moni...
- Metadata: {'scope': 'global', 'topic': 'argo_program', 'type': 'external_context'}

**Example 2:**
- ID: `context_indian_ocean_argo`
- Content: Indian Ocean ARGO Coverage:
Regional focus of this database
Float density: Variable, higher near major shipping routes  
Data period: 2000-present, with increasing coverage over time
Key contributors:...
- Metadata: {'region': 'indian_ocean', 'type': 'external_context', 'topic': 'regional_coverage'}

**Example 3:**
- ID: `context_data_standards`
- Content: ARGO Data Standards:
File Format: NetCDF (Network Common Data Format)
Quality Control: Automated + manual delayed mode QC
Spatial Resolution: Point measurements, irregular spacing
Temporal Resolution:...
- Metadata: {'type': 'external_context', 'topic': 'data_standards', 'technical': True}

---

