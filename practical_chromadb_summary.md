# Practical ARGO ChromaDB Summary

## Collection Information
- **Name**: argo_practical_queries
- **Total Query Patterns**: 42
- **Query Types**: 8

## Query Type Breakdown

### Statistics Query (8 patterns)

**Example 1:**
- ID: `stats_01`
- Content: User Query: "How many floats are in the database"
SQL: SELECT COUNT(*) as total_floats FROM floats;
Description: Count total number of floats
- Category: database_stats

**Example 2:**
- ID: `stats_02`
- Content: User Query: "How many profiles are available"
SQL: SELECT COUNT(*) as total_profiles FROM profiles;
Description: Count total number of profiles
- Category: database_stats

**Example 3:**
- ID: `stats_03`
- Content: User Query: "How many measurements are in total"
SQL: SELECT COUNT(*) as total_measurements FROM measurements;
Description: Count total number of measurements
- Category: database_stats

... and 5 more patterns

---

### Float Query (7 patterns)

**Example 1:**
- ID: `float_01`
- Content: User Query: "List all floats"
SQL: SELECT float_id, wmo_number, current_status, deployment_date, deployment_latitude, deployment_longitude FROM floats ORDER BY wmo_number;
Description: List all floats with basic information
- Category: float_operations

**Example 2:**
- ID: `float_02`
- Content: User Query: "Show active floats"
SQL: SELECT float_id, wmo_number, current_status, last_latitude, last_longitude, last_update FROM floats WHERE current_status = 'ACTIVE' ORDER BY last_update DESC;
Description: List only active/operational floats
- Category: float_operations

**Example 3:**
- ID: `float_03`
- Content: User Query: "Show dead or inactive floats"
SQL: SELECT float_id, wmo_number, current_status, last_update FROM floats WHERE current_status IN ('DEAD', 'INACTIVE') ORDER BY last_update DESC;
Description: List non-operational floats
- Category: float_operations

... and 4 more patterns

---

### Profile Query (7 patterns)

**Example 1:**
- ID: `profile_01`
- Content: User Query: "Show most recent profiles"
SQL: SELECT p.profile_id, p.float_id, p.profile_date, p.latitude, p.longitude, p.max_pressure FROM profiles p ORDER BY p.profile_date DESC LIMIT 10;
Description: List 10 most recent profiles
- Category: profile_operations

**Example 2:**
- ID: `profile_02`
- Content: User Query: "Show oldest profiles"
SQL: SELECT p.profile_id, p.float_id, p.profile_date, p.latitude, p.longitude FROM profiles p ORDER BY p.profile_date ASC LIMIT 10;
Description: List 10 oldest profiles
- Category: profile_operations

**Example 3:**
- ID: `profile_03`
- Content: User Query: "Profiles from specific float"
SQL: SELECT profile_id, cycle_number, profile_date, latitude, longitude, max_pressure FROM profiles WHERE float_id = ? ORDER BY profile_date DESC;
Description: Get all profiles from a specific float (use float_id parameter)
- Category: profile_operations

... and 4 more patterns

---

### Measurement Query (7 patterns)

**Example 1:**
- ID: `measurement_01`
- Content: User Query: "Surface temperature data"
SQL: SELECT p.profile_date, p.latitude, p.longitude, m.pressure, m.temperature FROM profiles p JOIN measurements m ON p.profile_id = m.profile_id WHERE m.pressure <= 10 AND m.temperature_qc <= 2 ORDER BY p.profile_date DESC LIMIT 100;
Description: Surface tempe...
- Category: data_extraction

**Example 2:**
- ID: `measurement_02`
- Content: User Query: "Deep water measurements"
SQL: SELECT p.profile_date, p.latitude, p.longitude, m.pressure, m.temperature, m.salinity FROM profiles p JOIN measurements m ON p.profile_id = m.profile_id WHERE m.pressure >= 1000 AND m.temperature_qc <= 2 AND m.salinity_qc <= 2 ORDER BY p.profile_date DESC L...
- Category: data_extraction

**Example 3:**
- ID: `measurement_03`
- Content: User Query: "Temperature and salinity by depth ranges"
SQL: SELECT CASE WHEN pressure <= 50 THEN 'Surface (0-50m)' WHEN pressure <= 200 THEN 'Upper (50-200m)' WHEN pressure <= 1000 THEN 'Mid (200-1000m)' ELSE 'Deep (>1000m)' END as depth_zone, COUNT(*) as measurements, AVG(temperature) as avg_temp, ...
- Category: data_extraction

... and 4 more patterns

---

### Quality Control Query (5 patterns)

**Example 1:**
- ID: `qc_01`
- Content: User Query: "Quality control statistics for temperature"
SQL: SELECT temperature_qc, COUNT(*) as count, ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM measurements WHERE temperature IS NOT NULL), 2) as percentage FROM measurements WHERE temperature IS NOT NULL GROUP BY temperature_qc ORDER BY temper...
- Category: data_quality

**Example 2:**
- ID: `qc_02`
- Content: User Query: "Quality control statistics for salinity"
SQL: SELECT salinity_qc, COUNT(*) as count, ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM measurements WHERE salinity IS NOT NULL), 2) as percentage FROM measurements WHERE salinity IS NOT NULL GROUP BY salinity_qc ORDER BY salinity_qc;
Descript...
- Category: data_quality

**Example 3:**
- ID: `qc_03`
- Content: User Query: "Good quality measurements count"
SQL: SELECT COUNT(*) as good_quality_measurements FROM measurements WHERE (temperature_qc <= 2 OR temperature IS NULL) AND (salinity_qc <= 2 OR salinity IS NULL);
Description: Count of measurements with good quality flags
- Category: data_quality

... and 2 more patterns

---

### Geographic Query (4 patterns)

**Example 1:**
- ID: `geo_01`
- Content: User Query: "Measurements in Arabian Sea region"
SQL: SELECT p.profile_date, p.latitude, p.longitude, m.temperature, m.salinity FROM profiles p JOIN measurements m ON p.profile_id = m.profile_id WHERE p.latitude BETWEEN 10 AND 25 AND p.longitude BETWEEN 50 AND 75 AND m.temperature_qc <= 2 ORDER BY p...
- Category: spatial_analysis

**Example 2:**
- ID: `geo_02`
- Content: User Query: "Measurements in Bay of Bengal region"
SQL: SELECT p.profile_date, p.latitude, p.longitude, m.temperature, m.salinity FROM profiles p JOIN measurements m ON p.profile_id = m.profile_id WHERE p.latitude BETWEEN 5 AND 25 AND p.longitude BETWEEN 80 AND 100 AND m.temperature_qc <= 2 ORDER BY...
- Category: spatial_analysis

**Example 3:**
- ID: `geo_03`
- Content: User Query: "Temperature statistics by region"
SQL: SELECT CASE WHEN longitude BETWEEN 50 AND 75 AND latitude BETWEEN 10 AND 25 THEN 'Arabian Sea' WHEN longitude BETWEEN 80 AND 100 AND latitude BETWEEN 5 AND 25 THEN 'Bay of Bengal' ELSE 'Other Indian Ocean' END as region, COUNT(*) as measurements, A...
- Category: spatial_analysis

... and 1 more patterns

---

### Schema Info (3 patterns)

**Example 1:**
- ID: `schema_floats`
- Content: FLOATS TABLE SCHEMA:
Primary Key: float_id (TEXT)
Key Columns: wmo_number (INTEGER), current_status (TEXT), deployment_date (TEXT)
Location: deployment_latitude (REAL), deployment_longitude (REAL)
Status Values: 'ACTIVE', 'DEAD', 'INACTIVE', 'UNKNOWN'
Relationships: floats.float_id -> profiles.float...
- Category: N/A

**Example 2:**
- ID: `schema_profiles`
- Content: PROFILES TABLE SCHEMA:
Primary Key: profile_id (INTEGER, auto-increment)
Foreign Key: float_id (TEXT) references floats.float_id
Key Columns: profile_date (TEXT), latitude (REAL), longitude (REAL)
Data Quality: data_quality_flag (INTEGER), data_mode (TEXT)
Relationships: profiles.profile_id -> measu...
- Category: N/A

**Example 3:**
- ID: `schema_measurements`
- Content: MEASUREMENTS TABLE SCHEMA:
Primary Key: measurement_id (INTEGER, auto-increment)
Foreign Key: profile_id (INTEGER) references profiles.profile_id
Core Data: pressure (REAL), temperature (REAL), salinity (REAL)
Quality Control: temperature_qc (INTEGER), salinity_qc (INTEGER)
QC Flags: 1=good, 2=proba...
- Category: N/A

---

### Performance Guide (1 patterns)

**Example 1:**
- ID: `performance_rules`
- Content: QUERY PERFORMANCE RULES:
1. ALWAYS filter profiles first, then JOIN measurements
2. Use quality control filters: temperature_qc <= 2, salinity_qc <= 2
3. Add LIMIT clauses to prevent large result sets
4. Use indexed columns: profile_date, latitude, longitude for profiles
5. Pattern: SELECT ... FROM ...
- Category: optimization

---

