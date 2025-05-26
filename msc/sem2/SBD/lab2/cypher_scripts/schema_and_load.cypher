// -----------------------------------------------------------------------------
// Constraints
// -----------------------------------------------------------------------------


// Airport Constraints
CREATE CONSTRAINT airport_iata_code_unique IF NOT EXISTS FOR (a:Airport) REQUIRE a.iata_code IS UNIQUE;
CREATE CONSTRAINT airline_iata_code_unique IF NOT EXISTS FOR (a:Airline) REQUIRE a.iata_code IS UNIQUE;
CREATE CONSTRAINT airline_icao_code_unique IF NOT EXISTS FOR (a:Airline) REQUIRE a.icao_code IS UNIQUE;
CREATE CONSTRAINT aircraft_registration_unique IF NOT EXISTS FOR (a:Aircraft) REQUIRE a.registration_number IS UNIQUE;

// Flight Constraints
CREATE CONSTRAINT flight_number_unique IF NOT EXISTS FOR (f:Flight) REQUIRE f.flight_number IS UNIQUE;

// Passenger Constraints
CREATE CONSTRAINT passenger_id_unique IF NOT EXISTS FOR (p:Passenger) REQUIRE p.passenger_id IS UNIQUE;

// Booking Constraints
CREATE CONSTRAINT booking_reference_unique IF NOT EXISTS FOR (b:Booking) REQUIRE b.booking_reference IS UNIQUE;

// Country Constraints
CREATE CONSTRAINT country_iso_code_unique IF NOT EXISTS FOR (c:Country) REQUIRE c.iso_code IS UNIQUE;
CREATE CONSTRAINT country_name_unique IF NOT EXISTS FOR (c:Country) REQUIRE c.name IS UNIQUE;

// -----------------------------------------------------------------------------
// Data population
// -----------------------------------------------------------------------------

// Load Countries
LOAD CSV WITH HEADERS FROM 'file:///countries.csv' AS row
CREATE (c:Country {iso_code: row.iso_code, name: row.name});

// Load Airports
LOAD CSV WITH HEADERS FROM 'file:///airports.csv' AS row
CREATE (a:Airport {
  iata_code: row.iata_code, 
  name: row.name, 
  city: row.city, 
  latitude: toFloat(row.latitude), 
  longitude: toFloat(row.longitude)
});

// Load Airlines
LOAD CSV WITH HEADERS FROM 'file:///airlines.csv' AS row
CREATE (al:Airline {
  iata_code: row.iata_code, 
  icao_code: row.icao_code, 
  name: row.name, 
  callsign: row.callsign
});

// Load Aircraft
LOAD CSV WITH HEADERS FROM 'file:///aircraft.csv' AS row
CREATE (ac:Aircraft {
  registration_number: row.registration_number, 
  type: row.type, 
  manufacturer: row.manufacturer, 
  seat_capacity: toInteger(row.seat_capacity)
});

// Load Flights
LOAD CSV WITH HEADERS FROM 'file:///flights.csv' AS row
CREATE (fl:Flight {
  flight_number: row.flight_number, 
  departure_datetime: datetime(row.departure_datetime), 
  arrival_datetime: datetime(row.arrival_datetime), 
  status: row.status
});

// Load Passengers
LOAD CSV WITH HEADERS FROM 'file:///passengers.csv' AS row
CREATE (p:Passenger {
  passenger_id: row.passenger_id, 
  first_name: row.first_name, 
  last_name: row.last_name, 
  frequent_flyer_number: row.frequent_flyer_number
});

// Load Bookings
LOAD CSV WITH HEADERS FROM 'file:///bookings.csv' AS row
CREATE (b:Booking {
  booking_reference: row.booking_reference, 
  seat_number: row.seat_number, 
  class_of_service: row.class_of_service
});

// -----------------------------------------------------------------------------
// Create Relationships
// -----------------------------------------------------------------------------

// Airport-Country Relationships
LOAD CSV WITH HEADERS FROM 'file:///airports.csv' AS row
MATCH (a:Airport {iata_code: row.iata_code})
MATCH (c:Country {iso_code: row.country_iso_code})
MERGE (a)-[:LOCATED_IN]->(c);

// Airline-Country and Airline-Hub Relationships
LOAD CSV WITH HEADERS FROM 'file:///airlines.csv' AS row
MATCH (al:Airline {iata_code: row.iata_code})
MATCH (c:Country {iso_code: row.country_iso_code})
MATCH (hub:Airport {iata_code: row.hub_airport_iata})
MERGE (al)-[:BASED_IN]->(c)
MERGE (al)-[:HAS_HUB]->(hub);

// Flight Relationships
LOAD CSV WITH HEADERS FROM 'file:///flights.csv' AS row
MATCH (fl:Flight {flight_number: row.flight_number})
MATCH (al:Airline {iata_code: row.airline_iata})
MATCH (dep_ap:Airport {iata_code: row.dep_airport_iata})
MATCH (arr_ap:Airport {iata_code: row.arr_airport_iata})
MATCH (ac:Aircraft {registration_number: row.aircraft_reg})
MERGE (al)-[:OPERATES_FLIGHT]->(fl)
MERGE (fl)-[:DEPARTS_FROM]->(dep_ap)
MERGE (fl)-[:ARRIVES_AT]->(arr_ap)
MERGE (fl)-[:USES_AIRCRAFT]->(ac);


// Passenger-Booking-Flight Relationships
LOAD CSV WITH HEADERS FROM 'file:///bookings.csv' AS row
MATCH (p:Passenger {passenger_id: row.passenger_id})
MATCH (b:Booking {booking_reference: row.booking_reference})
MATCH (fl:Flight {flight_number: row.flight_number})
MERGE (p)-[:HAS_BOOKING]->(b)
MERGE (b)-[:FOR_FLIGHT]->(fl);

// End of Data Population
