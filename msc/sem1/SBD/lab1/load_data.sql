USE AirlinesTemporalDB;
GO

/* Airports (10) */
INSERT INTO Airports (IATACode, Name, City, Country) VALUES
('WAW','Warsaw Chopin','Warsaw','Poland'),
('KRK','Kraków Balice','Kraków','Poland'),
('GDN','Gdańsk Lech Wałęsa','Gdańsk','Poland'),
('BER','Berlin BER','Berlin','Germany'),
('MUC','Munich','Munich','Germany'),
('LHR','Heathrow','London','UK'),
('CDG','Charles de Gaulle','Paris','France'),
('AMS','Schiphol','Amsterdam','Netherlands'),
('JFK','John F. Kennedy','New York','USA'),
('ORD','O''Hare','Chicago','USA');

/* Aircraft (5) */
INSERT INTO Aircraft (TailNumber, Model, Seats) VALUES
('SP-LAA','B737-800',186),
('SP-LAB','B737-800',186),
('SP-LAC','E190',106),
('SP-LAD','A321neo',230),
('SP-LAE','B787-9',294);

/* Routes (15) */
INSERT INTO Routes (OriginID, DestID, DistanceKm) VALUES
(1,4, 520),(1,5, 800),(1,6,1440),(1,7,1360),(1,8,1100),
(4,6, 930),(4,7,1050),(5,6, 460),(6,7,340),(6,8,370),
(8,6,370),(9,6,5570),(1,2,250),(2,3,470),(3,1,300);

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

/*  Create one fare per route/class (Y) */
INSERT INTO FarePricing(RouteID,CabinClass,PriceEUR)
SELECT RouteID,'Y', 0.12*DistanceKm FROM Routes;

/*  Create three future price changes per route */
UPDATE FarePricing SET PriceEUR = PriceEUR*1.10;  -- after our first update history is kept
DECLARE @r INT = 1;
WHILE @r<=15
BEGIN
   -- price drop next month
   UPDATE FarePricing SET PriceEUR = PriceEUR*0.9
   WHERE RouteID=@r; SET @r=@r+1; 
END

/* FlightSchedule: 25 planned flights - now with explicit arrival time */
INSERT INTO FlightSchedule (RouteID,AircraftID,ScheduledDepUTC,ScheduledArrUTC,Status)
SELECT 
    RouteID,
    AircraftID,
    DepTime,
    DATEADD(MINUTE, (SELECT DistanceKm FROM Routes WHERE RouteID = R.RouteID)/9.6, DepTime) AS ArrTime,
    'planned'
FROM (
    VALUES
    (1,1,'2024-06-15 05:00'),
    (2,2,'2024-06-15 06:30'),
    (3,3,'2024-06-15 07:00'),
    (4,4,'2024-06-16 11:00'),
    (5,5,'2024-06-16 22:00'),
    (6,1,'2024-06-17 05:00'),
    (7,2,'2024-06-17 08:00'),
    (8,3,'2024-06-17 09:00'),
    (9,4,'2024-06-17 12:00'),
    (10,5,'2024-06-17 13:00'),
    (11,1,'2024-06-18 05:00'),
    (12,2,'2024-06-18 07:00'),
    (13,3,'2024-06-18 09:00'),
    (14,4,'2024-06-18 15:00'),
    (15,5,'2024-06-18 18:00'),
    (1,1,'2024-07-01 05:00'),
    (2,2,'2024-07-01 06:30'),
    (3,3,'2024-07-02 07:00'),
    (4,4,'2024-07-02 11:00'),
    (5,5,'2024-07-02 22:00'),
    (6,1,'2024-07-03 05:00'),
    (7,2,'2024-07-03 08:00'),
    (8,3,'2024-07-03 10:00'),
    (9,4,'2024-07-03 12:00'),
    (10,5,'2024-07-03 14:00')
) AS R(RouteID, AircraftID, DepTime);

/* Seat inventory – assume full at start */
INSERT INTO SeatInventory (FlightID,CabinClass,SeatsLeft)
SELECT FlightID,'Y', (SELECT Seats FROM Aircraft WHERE AircraftID=F.AircraftID) * 0.9
FROM FlightSchedule F;

/* Crew assignments (sample) */
INSERT INTO CrewAssignment (FlightID,CrewMember,Role)
SELECT FlightID,'Captain '+RIGHT('0'+CAST(FlightID AS VARCHAR),2),'captain' FROM FlightSchedule;

/* Maintenance – aircraft 1 planned A-check next month (future!) */
/* We can't directly set ValidFrom/ValidTo, so we'll handle this differently */
INSERT INTO MaintenanceStatus (AircraftID,Status,Note) 
VALUES (1,'Scheduled A-check','Aircraft unavailable');

/* For simulating future maintenance, we can update with procedure */
EXEC sys.sp_set_session_context @key = N'LastMaintenanceDate', @value = '2024-07-10';
GO

/* Add a maintenance procedure to handle future dating */
CREATE OR ALTER PROCEDURE ScheduleMaintenance
    @AircraftID INT,
    @OriginalStatus NVARCHAR(30), /* The status we expect to transition FROM */
    @OriginalNote NVARCHAR(200), /* The note of the status we expect to transition FROM */
    @StartDate DATETIME2,    /* Corresponds to when maintenance was scheduled to start */
    @EndDate DATETIME2        /* Corresponds to when maintenance was scheduled to end */
AS
BEGIN
    -- This procedure marks a specific aircraft as 'In Service'
    -- assuming it was previously in @OriginalStatus.
    -- This will make the old status historical and the 'In Service' status current.

    IF EXISTS (SELECT 1 FROM MaintenanceStatus WHERE AircraftID = @AircraftID AND Status = @OriginalStatus AND ValidTo = '9999-12-31 23:59:59.9999999')
    BEGIN
        UPDATE MaintenanceStatus
        SET Status = 'In Service',
            Note = 'Aircraft returned from maintenance on ' + CONVERT(NVARCHAR, @EndDate, 120) + '. Original: ' + @OriginalNote
        WHERE AircraftID = @AircraftID AND Status = @OriginalStatus;
    END
    ELSE
    BEGIN
        PRINT 'Warning: Aircraft ' + CAST(@AircraftID AS NVARCHAR) + ' was not in status ' + @OriginalStatus + ' or was not the current record. Attempting to insert ''In Service'' status directly for ' + CONVERT(NVARCHAR, @EndDate, 120) + '.';
        -- Attempt to insert only if no current record for this aircraft exists, or if the update path wasn't taken.
        -- This part might still cause issues if another "current" record exists for this AircraftID that wasn't @OriginalStatus
        IF NOT EXISTS (SELECT 1 FROM MaintenanceStatus WHERE AircraftID = @AircraftID AND ValidTo = '9999-12-31 23:59:59.9999999')
        BEGIN
            INSERT INTO MaintenanceStatus (AircraftID, Status, Note)
            VALUES (@AircraftID, 'In Service', 'Aircraft set to In Service (original state ' + @OriginalStatus + ' not found as current) on ' + CONVERT(NVARCHAR, @EndDate, 120));
        END
        ELSE
        BEGIN
             PRINT 'Info: Aircraft ' + CAST(@AircraftID AS NVARCHAR) + ' already has a current maintenance status. ''In Service'' not inserted via fallback to prevent PK violation.';
        END
    END
END
GO

/* Schedule the maintenance */
/* The initial INSERT on line 102 sets (1, 'Scheduled A-check', 'Aircraft unavailable') */
/* So, we call the procedure to transition from that state. */
EXEC ScheduleMaintenance @AircraftID=1,
     @OriginalStatus='Scheduled A-check',
     @OriginalNote='Aircraft unavailable', /* This is the note from the INSERT on line 102 */
     @StartDate='2024-07-10',
     @EndDate='2024-07-20';
GO
