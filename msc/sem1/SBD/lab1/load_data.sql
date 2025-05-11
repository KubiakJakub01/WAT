USE AirlinesTemporalDB;
GO

/* Airports (20) */
INSERT INTO Airports (IATACode, Name, City, Country) VALUES
('WAW','Warsaw Chopin','Warsaw','Poland'),       -- ID 1
('KRK','Kraków Balice','Kraków','Poland'),       -- ID 2
('GDN','Gdańsk Lech Wałęsa','Gdańsk','Poland'),  -- ID 3
('BER','Berlin BER','Berlin','Germany'),        -- ID 4
('MUC','Munich','Munich','Germany'),            -- ID 5
('LHR','Heathrow','London','UK'),               -- ID 6
('CDG','Charles de Gaulle','Paris','France'),   -- ID 7
('AMS','Schiphol','Amsterdam','Netherlands'),   -- ID 8
('JFK','John F. Kennedy','New York','USA'),     -- ID 9
('ORD','O''Hare','Chicago','USA'),             -- ID 10
('FRA','Frankfurt Airport','Frankfurt','Germany'), -- ID 11
('MAD','Madrid Barajas','Madrid','Spain'),        -- ID 12
('BCN','Barcelona El Prat','Barcelona','Spain'),  -- ID 13
('FCO','Rome Fiumicino','Rome','Italy'),         -- ID 14 (Changed ROME to FCO)
('ZRH','Zurich Airport','Zurich','Switzerland'),-- ID 15
('VIE','Vienna Schwechat','Vienna','Austria'),    -- ID 16
('PRG','Prague Vaclav Havel','Prague','Czech Republic'), -- ID 17
('BUD','Budapest Liszt Ferenc','Budapest','Hungary'),-- ID 18
('DXB','Dubai International','Dubai','UAE'),      -- ID 19
('SIN','Singapore Changi','Singapore','Singapore');-- ID 20

/* Aircraft (20) */
INSERT INTO Aircraft (TailNumber, Model, Seats) VALUES
('SP-LAA','B737-800',186), ('SP-LAB','B737-800',186), ('SP-LAC','E190',106), ('SP-LAD','A321neo',230), ('SP-LAE','B787-9',294), -- Original 5 (IDs 1-5)
('SP-LAF','B737-MAX8',200), ('SP-LAG','A320neo',180), ('SP-LAH','E195-E2',132), ('SP-LAI','B787-8',252), ('SP-LAJ','A350-900',315), -- IDs 6-10
('D-AINA','A320neo',180), ('D-AINB','A321neo',230), ('G-XLEA','A350-1000',360), ('N101AA','B777-300ER',304),('N102AA','B787-9',285), -- IDs 11-15
('F-GTAA','A220-300',145), ('PH-BHA','B777-200ER',320), ('A6-EEA','A380-800',489), ('9V-SMA','A350-900',303), ('HB-JHA','CS100',125); -- IDs 16-20

/* Routes (20) */
INSERT INTO Routes (OriginID, DestID, DistanceKm) VALUES
(1,4, 520),(1,5, 800),(1,6,1440),(1,7,1360),(1,8,1100), -- Original using IDs 1-8
(4,6, 930),(4,7,1050),(5,6, 460),(6,7,340),(6,8,370),
(8,6,370),(9,6,5570),(1,2,250),(2,3,470),(3,1,300), -- Original 15 (IDs 1-15 in Routes table)
-- New Routes (IDs 16-20 in Routes table)
(11,12, 1800), -- Frankfurt (11) to Madrid (12)
(13,14, 720),  -- Barcelona (13) to Rome (14)
(15,16, 600),  -- Zurich (15) to Vienna (16)
(17,19, 4400), -- Prague (17) to Dubai (19)
(18,20, 8200); -- Budapest (18) to Singapore (20)

/* Passengers (20) */
INSERT INTO Passengers (FirstName,LastName,Email) VALUES
('Anna','Kowalska','anna@example.com'),('Jan','Nowak','jan@example.com'),
('Piotr','Zieliński','piotr@example.com'),('Maria','Lewandowska','maria@example.com'),
('John','Doe','john@example.com'),('Jane','Roe','jane@example.com'),
('Thomas','Müller','tm@example.com'),('Emily','Smith','es@example.com'),
('Lucas','Brown','lb@example.com'),('Olivia','Davis','od@example.com'),
('Noah','Wilson','nw@example.com'),('Mia','Taylor','mt@example.com'),
('Liam','Anderson','la@example.com'),('Emma','Thomas','et@example.com'),
('Sophia','Jackson','sj@example.com'),('James','White','jw@example.com'),
('Isabella','Harris','ih@example.com'),('Benjamin','Martin','bm@example.com'),
('Charlotte','Thompson','ct@example.com'),('Henry','Garcia','hg@example.com');

/*  Create one fare per route/class (Y) - covering all 20 routes */
INSERT INTO FarePricing(RouteID,CabinClass,PriceEUR)
SELECT RouteID,'Y', 0.12*DistanceKm FROM Routes;

/*  Create three future price changes per route - covering all 20 routes */
UPDATE FarePricing SET PriceEUR = PriceEUR*1.10;
DECLARE @r INT = 1;
DECLARE @TotalRoutes INT;
SELECT @TotalRoutes = COUNT(*) FROM Routes; -- Get total number of routes dynamically
WHILE @r <= @TotalRoutes
BEGIN
   UPDATE FarePricing SET PriceEUR = PriceEUR*0.9 WHERE RouteID=@r;
   SET @r=@r+1;
END

/* FlightSchedule: ~40 planned flights (original 25 + 15 new) */
INSERT INTO FlightSchedule (RouteID,AircraftID,ScheduledDepUTC,ScheduledArrUTC,Status)
SELECT
    RouteID, AircraftID, DepTime,
    DATEADD(MINUTE, (SELECT DistanceKm FROM Routes WHERE RouteID = R.RouteID)/9.6, DepTime) AS ArrTime,
    'planned'
FROM (
    VALUES -- Original 25 flights
    (1,1,'2024-06-15 05:00'), (2,2,'2024-06-15 06:30'), (3,3,'2024-06-15 07:00'),
    (4,4,'2024-06-16 11:00'), (5,5,'2024-06-16 22:00'), (6,1,'2024-06-17 05:00'),
    (7,2,'2024-06-17 08:00'), (8,3,'2024-06-17 09:00'), (9,4,'2024-06-17 12:00'),
    (10,5,'2024-06-17 13:00'),(11,1,'2024-06-18 05:00'),(12,2,'2024-06-18 07:00'),
    (13,3,'2024-06-18 09:00'),(14,4,'2024-06-18 15:00'),(15,5,'2024-06-18 18:00'),
    (1,1,'2024-07-01 05:00'), (2,2,'2024-07-01 06:30'), (3,3,'2024-07-02 07:00'),
    (4,4,'2024-07-02 11:00'), (5,5,'2024-07-02 22:00'), (6,1,'2024-07-03 05:00'),
    (7,2,'2024-07-03 08:00'), (8,3,'2024-07-03 10:00'), (9,4,'2024-07-03 12:00'),
    (10,5,'2024-07-03 14:00'),
    -- New 15 flights using new routes and aircraft
    (16,6,'2024-08-01 10:00'), (17,7,'2024-08-01 12:00'), (18,8,'2024-08-02 14:00'),
    (19,9,'2024-08-02 16:00'), (20,10,'2024-08-03 18:00'),(16,11,'2024-08-04 10:00'),
    (17,12,'2024-08-04 12:00'),(18,13,'2024-08-05 14:00'),(19,14,'2024-08-05 16:00'),
    (20,15,'2024-08-06 18:00'),(1,16,'2024-08-07 08:00'),  (4,17,'2024-08-07 09:00'),
    (6,18,'2024-08-08 11:00'), (9,19,'2024-08-08 15:00'), (10,20,'2024-08-09 17:00')
) AS R(RouteID, AircraftID, DepTime);

/* Seat inventory – assume full at start - will reflect new flights */
INSERT INTO SeatInventory (FlightID,CabinClass,SeatsLeft)
SELECT FlightID,'Y', (SELECT Seats FROM Aircraft WHERE AircraftID=F.AircraftID) * 0.9
FROM FlightSchedule F;

/* Crew assignments (sample) - will reflect new flights */
INSERT INTO CrewAssignment (FlightID,CrewMember,Role)
SELECT FlightID,'Captain '+RIGHT('00'+CAST(FlightID AS VARCHAR),3),'captain' FROM FlightSchedule F; -- Adjusted for more flight IDs
SELECT FlightID,'FO '+RIGHT('00'+CAST(FlightID AS VARCHAR),3),'first_officer' FROM FlightSchedule F WHERE FlightID % 2 = 0;
INSERT INTO CrewAssignment (FlightID,CrewMember,Role)
SELECT FlightID,'Purser '+RIGHT('00'+CAST(FlightID AS VARCHAR),3),'purser' FROM FlightSchedule F WHERE FlightID % 3 = 0;


/* Maintenance Status - adding more records for >20 total */
-- Original for AircraftID 1
INSERT INTO MaintenanceStatus (AircraftID,Status,Note) VALUES (1,'Scheduled A-check','Aircraft unavailable');
-- This will be updated by the ScheduleMaintenance procedure later

-- Add initial 'In Service' for several new aircraft
INSERT INTO MaintenanceStatus (AircraftID, Status, Note) VALUES (6, 'In Service', 'New aircraft, initial status.');
INSERT INTO MaintenanceStatus (AircraftID, Status, Note) VALUES (7, 'In Service', 'New aircraft, initial status.');
INSERT INTO MaintenanceStatus (AircraftID, Status, Note) VALUES (8, 'In Service', 'New aircraft, initial status.');
INSERT INTO MaintenanceStatus (AircraftID, Status, Note) VALUES (11, 'In Service', 'New aircraft, initial status.');
INSERT INTO MaintenanceStatus (AircraftID, Status, Note) VALUES (12, 'In Service', 'New aircraft, initial status.');
INSERT INTO MaintenanceStatus (AircraftID, Status, Note) VALUES (13, 'In Service', 'New aircraft, initial status.');
INSERT INTO MaintenanceStatus (AircraftID, Status, Note) VALUES (14, 'In Service', 'New aircraft, initial status.');
INSERT INTO MaintenanceStatus (AircraftID, Status, Note) VALUES (15, 'In Service', 'New aircraft, initial status.');


-- Add history for a few aircraft (AircraftID 9, 10, 16, 17, 18)
-- Each sequence adds 4 records to history + 1 current = 5 total per aircraft here. 5*5 = 25 records.
DECLARE @AircraftForMaint INT;
SET @AircraftForMaint = 9;
WHILE @AircraftForMaint <= 18 -- Process aircraft 9, 10, 16, 17, 18 for varied history
BEGIN
    IF @AircraftForMaint IN (9,10,16,17,18)
    BEGIN
        INSERT INTO MaintenanceStatus (AircraftID, Status, Note) VALUES (@AircraftForMaint, 'In Service', 'Initial operational status.');
        WAITFOR DELAY '00:00:00.010'; -- Tiny delay to ensure distinct ValidFrom for subsequent updates
        UPDATE MaintenanceStatus SET Status = 'Scheduled B-check', Note = 'Upcoming scheduled B-check' WHERE AircraftID = @AircraftForMaint AND Status = 'In Service';
        WAITFOR DELAY '00:00:00.010';
        UPDATE MaintenanceStatus SET Status = 'In Maintenance', Note = 'Undergoing B-check' WHERE AircraftID = @AircraftForMaint AND Status = 'Scheduled B-check';
        WAITFOR DELAY '00:00:00.010';
        UPDATE MaintenanceStatus SET Status = 'In Service', Note = 'Returned from B-check, fully operational' WHERE AircraftID = @AircraftForMaint AND Status = 'In Maintenance';
    END
    SET @AircraftForMaint = @AircraftForMaint + 1;
END

/* For simulating future maintenance, we can update with procedure - unchanged for AircraftID 1 */
EXEC sys.sp_set_session_context @key = N'LastMaintenanceDate', @value = '2024-07-10';
GO
/* Add a maintenance procedure to handle future dating - unchanged */
CREATE OR ALTER PROCEDURE ScheduleMaintenance
    @AircraftID INT, @OriginalStatus NVARCHAR(30), @OriginalNote NVARCHAR(200),
    @StartDate DATETIME2, @EndDate DATETIME2
AS
BEGIN
    IF EXISTS (SELECT 1 FROM MaintenanceStatus WHERE AircraftID = @AircraftID AND Status = @OriginalStatus AND ValidTo = '9999-12-31 23:59:59.9999999')
    BEGIN
        UPDATE MaintenanceStatus
        SET Status = 'In Service', Note = 'Aircraft returned from maintenance on ' + CONVERT(NVARCHAR, @EndDate, 120) + '. Original: ' + @OriginalNote
        WHERE AircraftID = @AircraftID AND Status = @OriginalStatus;
    END
    ELSE
    BEGIN
        PRINT 'Warning: Aircraft ' + CAST(@AircraftID AS NVARCHAR) + ' was not in status ' + @OriginalStatus + ' or was not the current record...';
        IF NOT EXISTS (SELECT 1 FROM MaintenanceStatus WHERE AircraftID = @AircraftID AND ValidTo = '9999-12-31 23:59:59.9999999')
        BEGIN
            INSERT INTO MaintenanceStatus (AircraftID, Status, Note)
            VALUES (@AircraftID, 'In Service', 'Aircraft set to In Service (original state ' + @OriginalStatus + ' not found as current) on ' + CONVERT(NVARCHAR, @EndDate, 120));
        END
        ELSE BEGIN PRINT 'Info: Aircraft ' + CAST(@AircraftID AS NVARCHAR) + ' already has a current maintenance status...'; END
    END
END
GO
EXEC ScheduleMaintenance @AircraftID=1, @OriginalStatus='Scheduled A-check',
     @OriginalNote='Aircraft unavailable', @StartDate='2024-07-10', @EndDate='2024-07-20';
GO

/* Bookings (20 records) */
INSERT INTO Bookings (PassengerID, RouteID, BookingDate) VALUES
(1,1,'2024-04-01'), (2,1,'2024-04-02'), (3,2,'2024-04-03'), (4,2,'2024-04-04'), (5,3,'2024-04-05'),
(6,4,'2024-04-06'), (7,5,'2024-04-07'), (8,6,'2024-04-08'), (9,7,'2024-04-09'), (10,8,'2024-04-10'),
(11,9,'2024-05-01'), (12,10,'2024-05-02'),(13,11,'2024-05-03'),(14,12,'2024-05-04'),(15,13,'2024-05-05'),
(16,14,'2024-05-06'),(17,15,'2024-05-07'),(18,16,'2024-05-08'),(19,17,'2024-05-09'),(20,18,'2024-05-10');

/* Tickets (20 records) - linking to Bookings */
-- Assuming FarePaid is derived somehow, for simplicity setting fixed values or linking to FarePricing at booking time
-- For simplicity, I will just add some sample values. A real system would fetch price at booking time.
INSERT INTO Tickets (BookingID, SeatNumber, FarePaid) VALUES
(1,'10A',120.50), (2,'10B',120.50), (3,'12C',150.00), (4,'12D',150.00), (5,'14E',90.75),
(6,'1A',200.00), (7,'2B',250.00), (8,'3C',180.00), (9,'4D',300.00), (10,'5E',220.00),
(11,'6A',400.00),(12,'7B',550.00),(13,'8C',600.00),(14,'9D',700.00),(15,'10E',650.00),
(16,'11A',80.00),(17,'12B',900.00),(18,'13C',1500.00),(19,'14D',1200.00),(20,'15E',2000.00);

PRINT 'Data loading script completed with additional data.';
GO
