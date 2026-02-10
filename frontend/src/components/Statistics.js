import React, { useState, useEffect } from 'react';
import { Presentation, Users2, Library, Trophy, Rocket, Sparkles, GraduationCap } from 'lucide-react';
import { ComposableMap, Geographies, Geography, Marker, Line } from 'react-simple-maps';
import '../styles/statistics.css';

const geoUrl = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json";

const Statistics = () => {
  const [, setCounts] = useState({
    lectures: 0,
    educators: 0,
    subjects: 0,
    satisfaction: 0
  });

  useEffect(() => {
    // Animate numbers when component mounts
    const animate = () => {
      setCounts({
        lectures: 50000,
        educators: 10000,
        subjects: 200,
        satisfaction: 99
      });
    };

    const timer = setTimeout(animate, 300);
    return () => clearTimeout(timer);
  }, []);

  const stats = [
    {
      icon: Presentation,
      color: '#3b82f6',
      number: '50,000+',
      label: 'Lectures Generated',
      description: 'Professional materials created'
    },
    {
      icon: Users2,
      color: '#8b5cf6',
      number: '10,000+',
      label: 'Educators Worldwide',
      description: 'Teachers trust Teach Genie'
    },
    {
      icon: Library,
      color: '#f59e0b',
      number: '200+',
      label: 'Subject Categories',
      description: 'Comprehensive coverage'
    },
    {
      icon: Trophy,
      color: '#10b981',
      number: '99.9%',
      label: 'Tutor Satisfaction',
      description: 'Rated by educators'
    }
  ];

  // Educator locations
  const locations = [
    { name: 'San Francisco', coordinates: [-122.4194, 37.7749], count: '2.5K' },
    { name: 'London', coordinates: [-0.1278, 51.5074], count: '1.8K' },
    { name: 'New Delhi', coordinates: [77.2090, 28.6139], count: '2.1K' },
    { name: 'Sydney', coordinates: [151.2093, -33.8688], count: '950' },
    { name: 'São Paulo', coordinates: [-46.6333, -23.5505], count: '1.2K' },
    { name: 'Tokyo', coordinates: [139.6917, 35.6895], count: '1.4K' },
  ];

  // Connection lines
  const connections = [
    { start: [-122.4194, 37.7749], end: [-0.1278, 51.5074] }, // SF to London
    { start: [-0.1278, 51.5074], end: [77.2090, 28.6139] }, // London to Delhi
    { start: [77.2090, 28.6139], end: [139.6917, 35.6895] }, // Delhi to Tokyo
    { start: [-122.4194, 37.7749], end: [-46.6333, -23.5505] }, // SF to São Paulo
    { start: [151.2093, -33.8688], end: [77.2090, 28.6139] }, // Sydney to Delhi
  ];

  return (
    <section className="statistics">
      <div className="container">


        {/* World Map Section */}
        <div className="world-map-section">
          <div className="statistics-header">
            <h2>
              Global Educator Network
            </h2>
            <p>Connecting teachers across continents</p>
          </div>

          <div className="world-map-container">
            <ComposableMap
              projection="geoMercator"
              projectionConfig={{
                scale: 160,
                center: [10, 20],
              }}
              height={600}
            >
              <Geographies geography={geoUrl}>
                {({ geographies }) =>
                  geographies
                    .filter((geo) => geo.properties.name !== 'Antarctica')
                    .map((geo) => (
                      <Geography
                        key={geo.rsmKey}
                        geography={geo}
                        fill="#9CA3AF"
                        stroke="#6B7280"
                        strokeWidth={0.8}
                        style={{
                          default: { outline: 'none' },
                          hover: { fill: '#6B7280', outline: 'none' },
                          pressed: { outline: 'none' },
                        }}
                      />
                    ))
                }
              </Geographies>

              {/* Connection Lines */}
              {connections.map((conn, i) => (
                <Line
                  key={`line-${i}`}
                  from={conn.start}
                  to={conn.end}
                  stroke="#EA580C"
                  strokeWidth={2}
                  strokeLinecap="round"
                  strokeOpacity={0.8}
                  className="connection-line"
                />
              ))}

              {/* Location Markers */}
              {locations.map(({ name, coordinates, count }) => (
                <Marker key={name} coordinates={coordinates}>
                  <g className="location-marker">
                    <circle r={8} fill="#1E3A8A" className="marker-pulse" />
                    <circle r={5} fill="#F59E0B" />
                    <text
                      textAnchor="middle"
                      y={-15}
                      style={{
                        fontSize: '10px',
                        fill: '#1F2937',
                        fontWeight: '600',
                      }}
                    >
                      {count}
                    </text>
                  </g>
                </Marker>
              ))}
            </ComposableMap>
          </div>
        </div>

        <div className="statistics-header">
          <h2>
            Trusted by Educators Worldwide
          </h2>
          <p>See why thousands of teachers choose Teach Genie for lesson planning</p>
        </div>

        <div className="stats-grid">
          {stats.map((stat, index) => (
            <div key={index} className="stat-card">
              <div className="stat-icon-wrapper" style={{ background: `linear-gradient(135deg, ${stat.color}15, ${stat.color}30)` }}>
                <stat.icon size={40} strokeWidth={2.5} style={{ color: stat.color }} />
              </div>
              <div className="stat-number">{stat.number}</div>
              <h3 className="stat-label">{stat.label}</h3>
              <p className="stat-description">{stat.description}</p>
            </div>
          ))}
        </div>

        <div className="statistics-highlight">
          <div className="highlight-item">
            <div className="highlight-icon-wrapper">
              <Rocket className="highlight-icon" size={40} strokeWidth={2.5} />
            </div>
            <h3>Lightning Fast</h3>
            <p>Get professional materials in under 2 minutes</p>
          </div>
          <div className="highlight-item">
            <div className="highlight-icon-wrapper">
              <Sparkles className="highlight-icon" size={40} strokeWidth={2.5} />
            </div>
            <h3>AI-Powered Discovery</h3>
            <p>Agents search thousands of academic resources</p>
          </div>
          <div className="highlight-item">
            <div className="highlight-icon-wrapper">
              <GraduationCap className="highlight-icon" size={40} strokeWidth={2.5} />
            </div>
            <h3>All Levels</h3>
            <p>From school to postgraduate education</p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Statistics;
