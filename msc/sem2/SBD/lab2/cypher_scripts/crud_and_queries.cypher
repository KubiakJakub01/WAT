// -----------------------------------------------------------------------------
// CREATE Operations
// -----------------------------------------------------------------------------

// C1: Create a new Airport
MERGE (country:Country {iso_code: 'ES', name: 'Spain'})
WITH country
CREATE (mad:Airport {
  iata_code: 'MAD', 
  name: 'Adolfo Suárez Madrid–Barajas Airport', 
  city: 'Madrid', 
  latitude: 40.493556, 
  longitude: -3.566764
})
MERGE (mad)-[:LOCATED_IN]->(country);

// C2: Create a new Passenger
CREATE (p:Passenger {
  passenger_id: 'P00007', 
  first_name: 'Luisa', 
  last_name: 'Martinez', 
  frequent_flyer_number: 'IB123456'
});

// C3: Create a new Flight and its relationships
MATCH (lh:Airline {iata_code: 'LH'})
MATCH (fra:Airport {iata_code: 'FRA'})
MATCH (jfk:Airport {iata_code: 'JFK'})
MATCH (aircraft:Aircraft {registration_number: 'D-ABYA'})
MERGE (fl:Flight {
  flight_number: 'LH404', 
  departure_datetime: datetime('2024-06-01T10:00:00Z'), 
  arrival_datetime: datetime('2024-06-01T13:00:00Z'), 
  status: 'Scheduled'
})
MERGE (lh)-[:OPERATES_FLIGHT]->(fl)
MERGE (fl)-[:DEPARTS_FROM]->(fra)
MERGE (fl)-[:ARRIVES_AT]->(jfk)
MERGE (fl)-[:USES_AIRCRAFT]->(aircraft);

// C4: Create a new Booking for an existing Passenger and Flight
MATCH (p:Passenger {passenger_id: 'P00001'})
MATCH (f:Flight {flight_number: 'LH404'})
MERGE (b:Booking {
  booking_reference: 'BK008',
  seat_number: '10A',
  class_of_service: 'Business'
})
MERGE (p)-[:HAS_BOOKING]->(b)
MERGE (b)-[:FOR_FLIGHT]->(f);

// -----------------------------------------------------------------------------
// READ Operations
// -----------------------------------------------------------------------------

// R1: Find an airport by its IATA code
MATCH (a:Airport {iata_code: 'JFK'})
RETURN a.name, a.city;

// R2: Find all airports in a specific country (e.g., Germany)
MATCH (a:Airport)-[:LOCATED_IN]->(c:Country {name: 'Germany'})
RETURN a.name, a.city, a.iata_code;

// R3: Get details of a specific flight including airline and airports
MATCH (al:Airline)-[:OPERATES_FLIGHT]->(f:Flight {flight_number: 'BA245'})
MATCH (f)-[:DEPARTS_FROM]->(dep_ap:Airport)
MATCH (f)-[:ARRIVES_AT]->(arr_ap:Airport)
RETURN f.flight_number, 
       al.name AS airline_name, 
       f.departure_datetime, dep_ap.name AS departure_airport, 
       f.arrival_datetime, arr_ap.name AS arrival_airport, 
       f.status;

// R4: Find all passengers with a last name 'Doe'
MATCH (p:Passenger {last_name: 'Doe'})
RETURN p.first_name, p.last_name, p.passenger_id, p.frequent_flyer_number;

// R5: Find all flights operated by a specific airline (e.g., Lufthansa)
MATCH (al:Airline {name: 'Lufthansa'})-[:OPERATES_FLIGHT]->(f:Flight)
RETURN f.flight_number, f.departure_datetime, f.arrival_datetime, f.status;

// -----------------------------------------------------------------------------
// UPDATE Operations
// -----------------------------------------------------------------------------

// U1: Update the status of a flight (e.g., flight AA100 is now 'Delayed')
MATCH (f:Flight {flight_number: 'AA100'})
SET f.status = 'Delayed',
    f.departure_datetime = f.departure_datetime + duration({hours: 1})
RETURN f.flight_number, f.status, f.departure_datetime;

// U2: Change a passenger's frequent flyer number
MATCH (p:Passenger {passenger_id: 'P00002'})
SET p.frequent_flyer_number = 'BA987654'
RETURN p.first_name, p.last_name, p.frequent_flyer_number;

// U3: Update an airport's name
MATCH (a:Airport {iata_code: 'MUC'})
SET a.name = 'Franz Josef Strauss Airport Munich'
RETURN a.iata_code, a.name;

// U4: Change the aircraft for a flight
MATCH (f:Flight {flight_number: 'LO3923'})
MATCH (new_aircraft:Aircraft {registration_number: 'N202DL'})
OPTIONAL MATCH (f)-[r:USES_AIRCRAFT]->(old_aircraft)
DELETE r
WITH f, new_aircraft
MERGE (f)-[:USES_AIRCRAFT]->(new_aircraft)
RETURN f.flight_number, new_aircraft.registration_number;

// -----------------------------------------------------------------------------
// DELETE Operations
// -----------------------------------------------------------------------------

// D1: Delete a passenger and their bookings
MATCH (p:Passenger {passenger_id: 'P00007'})
OPTIONAL MATCH (p)-[:HAS_BOOKING]->(b:Booking)
DETACH DELETE b, p;

// D2: Cancel a flight (delete the Flight node and its direct operational relationships)
MATCH (f:Flight {flight_number: 'AF10'})
DETACH DELETE f;

// D3: Remove an aircraft from service (delete the Aircraft node)
MATCH (ac:Aircraft {registration_number: 'SP-LRA'})
DETACH DELETE ac;

// -----------------------------------------------------------------------------
// Advanced Queries
// -----------------------------------------------------------------------------

// AQ6: Find shortest flight path between two airports (e.g., JFK to MUC) by number of flights (hops).
MATCH (start_ap:Airport {iata_code: 'JFK'}), (end_ap:Airport {iata_code: 'MUC'})
CALL {
  WITH start_ap, end_ap
  MATCH path = allShortestPaths((start_ap)-[:DEPARTS_FROM|ARRIVES_AT*]-(end_ap))
  RETURN path
}
RETURN path;

// AQ7: Find passengers who have flown on a specific airline (e.g., British Airways) more than once.
MATCH (p:Passenger)-[:HAS_BOOKING]->(:Booking)-[:FOR_FLIGHT]->(fl:Flight)<-[:OPERATES_FLIGHT]-(al:Airline {name: 'British Airways'})
WITH p, count(fl) AS flight_count
WHERE flight_count > 1
RETURN p.first_name, p.last_name, flight_count ORDER BY flight_count DESC;

// AQ8: Suggest connecting flights (flights departing from arrival airport of a given flight within a time window).
MATCH (f1:Flight {flight_number: 'AA100'})-[:ARRIVES_AT]->(connecting_ap:Airport)
WITH f1, connecting_ap, f1.arrival_datetime AS f1_arrival_time
MATCH (connecting_flight:Flight)-[:DEPARTS_FROM]->(connecting_ap)
WHERE connecting_flight.departure_datetime > f1_arrival_time + duration({hours: 1}) 
  AND connecting_flight.departure_datetime < f1_arrival_time + duration({hours: 4})
RETURN f1.flight_number AS initial_flight, 
       connecting_ap.name AS connecting_airport, 
       connecting_flight.flight_number AS connecting_flight_num, 
       connecting_flight.departure_datetime AS connecting_flight_departure;

// AQ9: Count number of flights per airline, order by count descending.
MATCH (al:Airline)-[:OPERATES_FLIGHT]->(f:Flight)
RETURN al.name AS airline_name, count(f) AS number_of_flights
ORDER BY number_of_flights DESC;

// AQ10: Calculate average flight duration for flights between two specific airports (e.g. LHR to JFK).
MATCH (:Airport {iata_code: 'LHR'})<-[:DEPARTS_FROM]-(f:Flight)-[:ARRIVES_AT]->(:Airport {iata_code: 'JFK'})
WHERE f.arrival_datetime IS NOT NULL AND f.departure_datetime IS NOT NULL
RETURN avg(duration.between(f.departure_datetime, f.arrival_datetime)) AS average_duration;

// AQ11: Find all Boeing aircraft with more than 200 seats, and list any flights they operate.
MATCH (ac:Aircraft)-[:USES_AIRCRAFT]-(fl:Flight)
WHERE ac.manufacturer = 'Boeing' AND ac.seat_capacity > 200
RETURN ac.registration_number, ac.type, ac.seat_capacity, fl.flight_number, fl.status
ORDER BY ac.registration_number, fl.flight_number;

// AQ12: List all passengers and the count of countries they have booked flights to.
MATCH (p:Passenger)-[:HAS_BOOKING]->(:Booking)-[:FOR_FLIGHT]->(f:Flight)-[:ARRIVES_AT]->(ap:Airport)-[:LOCATED_IN]->(c:Country)
RETURN p.first_name, p.last_name, count(DISTINCT c.name) AS countries_visited_count
ORDER BY countries_visited_count DESC, p.last_name;

// AQ13: Use MERGE to add a new 'Alliance' node and connect airlines to it.
MERGE (sa:Alliance {name: 'Star Alliance'})
WITH sa
MATCH (lh:Airline {iata_code: 'LH'})
MATCH (ac:Airline {iata_code: 'AC'})
MATCH (ua:Airline {iata_code: 'UA'})
MERGE (lh)-[:MEMBER_OF]->(sa)
MERGE (ac)-[:MEMBER_OF]->(sa)
MERGE (ua)-[:MEMBER_OF]->(sa)
WITH *
MATCH (al:Airline)-[:MEMBER_OF]->(alliance:Alliance)
RETURN al.name, alliance.name;

// AQ14: Use FOREACH to update a property on a list of nodes based on a condition.
MATCH (acs:Aircraft {type: 'Boeing 737-800'})
WITH collect(acs) AS aircraft_to_update
FOREACH (ac IN aircraft_to_update | SET ac.maintenance_status = 'Undergoing Maintenance')
WITH *
MATCH (ac:Aircraft {type: 'Boeing 737-800'})
RETURN ac.registration_number, ac.maintenance_status;

// AQ15: Find countries that are hubs for more than one airline in the database.
MATCH (c:Country)<-[:BASED_IN]-(al:Airline)-[:HAS_HUB]->(hub:Airport)-[:LOCATED_IN]->(c)
WITH c, count(DISTINCT al) AS num_airlines_hubbed
WHERE num_airlines_hubbed > 0
RETURN c.name AS country_name, num_airlines_hubbed
ORDER BY num_airlines_hubbed DESC;

// AQ16 (Actual GDS): Airport Importance using PageRank
// Step 1: Project a graph into the GDS catalog.
CALL gds.graph.project.cypher(
  'airportsPageRankGraph',
  'MATCH (a:Airport) RETURN id(a) AS id',
  'MATCH (a1:Airport)<-[:DEPARTS_FROM]-(f:Flight)-[:ARRIVES_AT]->(a2:Airport) RETURN id(a1) AS source, id(a2) AS target',
  {validateRelationships: false}
)
YIELD graphName AS projectedGraphName, nodeCount, relationshipCount;

// Step 2: Run the PageRank algorithm on the projected graph.
CALL gds.pageRank.stream('airportsPageRankGraph')
YIELD nodeId, score
WITH gds.util.asNode(nodeId) AS airport, score
RETURN airport.name AS airport_name, airport.iata_code, score
ORDER BY score DESC
LIMIT 10;

// Step 3: Drop the projected graph from the catalog when done.
CALL gds.graph.drop('airportsPageRankGraph');

// AQ18: Passengers and their Multi-Hop Journeys to a Specific Country (e.g., United States)
MATCH (p:Passenger)-[b_rel:HAS_BOOKING]->(b:Booking)-[f_rel:FOR_FLIGHT]->(f:Flight),
      (f)-[arr_rel:ARRIVES_AT]->(arr_ap:Airport)-[loc_rel:LOCATED_IN]->(c:Country {name: 'United States'})
OPTIONAL MATCH (f)-[dep_rel:DEPARTS_FROM]->(dep_ap:Airport)
OPTIONAL MATCH (al:Airline)-[op_rel:OPERATES_FLIGHT]->(f)
RETURN p, b, f, arr_ap, c, dep_ap, al, b_rel, f_rel, arr_rel, loc_rel, dep_rel, op_rel
LIMIT 50;

// AQ19: Add or Update Service Quality for Airports in a specific country
MATCH (a:Airport)-[:LOCATED_IN]->(c:Country {name: 'United States'})
WITH a
MERGE (a)-[r:HAS_SERVICE_QUALITY]->(sq:ServiceQuality)
ON CREATE SET sq.rating = 3, sq.description = 'Standard', sq.last_inspected = datetime()
ON MATCH SET sq.last_inspected = datetime()
RETURN a.name, sq.rating, sq.description, sq.last_inspected;

// AQ20: Identify and Tag VIP Passengers
MATCH (p:Passenger)-[:HAS_BOOKING]->(b:Booking)
WHERE b.class_of_service IN ['Business', 'First']
WITH p, count(b) AS premium_bookings_count
WHERE premium_bookings_count >= 2
WITH collect(p) AS vip_passengers_to_tag
FOREACH (passenger IN vip_passengers_to_tag | SET passenger:VIP)
WITH *
MATCH (vip:Passenger:VIP)
RETURN vip.passenger_id, vip.first_name, vip.last_name;
