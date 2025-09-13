import React, { useEffect, useRef, useState } from 'react';
import Globe from 'react-globe.gl';

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
  pagination: any;
  query_metadata: any;
}

interface Props {
  floatData: FloatData[];
  queryResult: QueryResult | null;
}

const OceanographicGlobe: React.FC<Props> = ({ floatData, queryResult }) => {
  const globeEl = useRef<any>(null);
  const [globeReady, setGlobeReady] = useState(false);

  useEffect(() => {
    if (globeEl.current && floatData.length > 0) {
      // Auto-rotate the globe
      globeEl.current.controls().autoRotate = true;
      globeEl.current.controls().autoRotateSpeed = 0.5;
      setGlobeReady(true);
    }
  }, [floatData]);

  // Convert float data to globe points
  const globePoints = floatData.map(float => ({
    ...float,
    lat: float.latitude,
    lng: float.longitude,
    color: float.avg_temperature ? 
      (float.avg_temperature > 20 ? '#ff4444' : 
       float.avg_temperature > 10 ? '#ffaa44' : '#4444ff') : '#888888',
    altitude: 0.05,
    label: `Float ${float.float_id}<br/>Profiles: ${float.profiles_count}<br/>Avg Temp: ${float.avg_temperature?.toFixed(1)}°C || 'N/A'}`
  }));

  const handlePointClick = (point: any) => {
    console.log('Float clicked:', point);
    // You could add a callback here to show float details
  };

  if (!globeReady && floatData.length === 0) {
    return (
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center', 
        height: '100%',
        flexDirection: 'column'
      }}>
        <div>Loading 3D Globe...</div>
        <div style={{ fontSize: '0.8em', marginTop: '10px', color: '#666' }}>
          Initializing WebGL and loading ARGO float data
        </div>
      </div>
    );
  }

  return (
    <Globe
      ref={globeEl}
      globeImageUrl="//unpkg.com/three-globe/example/img/earth-blue-marble.jpg"
      backgroundImageUrl="//unpkg.com/three-globe/example/img/night-sky.png"
      
      // ARGO float points
      pointsData={globePoints}
      pointLat="lat"
      pointLng="lng"
      pointColor="color"
      pointAltitude="altitude"
      pointRadius={0.8}
      pointLabel="label"
      onPointClick={handlePointClick}
      
      // Animation settings
      animateIn={true}
      waitForGlobeReady={true}
    />
  );
};

export default OceanographicGlobe;