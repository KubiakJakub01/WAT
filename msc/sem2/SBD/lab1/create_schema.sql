/* ---------------------------------------------------------
   5.1  Create the database
--------------------------------------------------------- */
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'AirlinesTemporalDB')
BEGIN
    CREATE DATABASE AirlinesTemporalDB;
    ALTER DATABASE AirlinesTemporalDB SET RECOVERY SIMPLE;
END
GO
USE AirlinesTemporalDB;
GO

/* First drop existing tables if they exist (in correct order) */
IF OBJECT_ID('dbo.CrewAssignment', 'U') IS NOT NULL 
BEGIN
    IF OBJECTPROPERTY(OBJECT_ID('dbo.CrewAssignment', 'U'), 'TableTemporalType') = 2
        ALTER TABLE dbo.CrewAssignment SET (SYSTEM_VERSIONING = OFF);
    DROP TABLE IF EXISTS dbo.CrewAssignment_History;
    DROP TABLE dbo.CrewAssignment;
END

IF OBJECT_ID('dbo.MaintenanceStatus', 'U') IS NOT NULL 
BEGIN
    IF OBJECTPROPERTY(OBJECT_ID('dbo.MaintenanceStatus', 'U'), 'TableTemporalType') = 2
        ALTER TABLE dbo.MaintenanceStatus SET (SYSTEM_VERSIONING = OFF);
    DROP TABLE IF EXISTS dbo.MaintenanceStatus_History;
    DROP TABLE dbo.MaintenanceStatus;
END

IF OBJECT_ID('dbo.SeatInventory', 'U') IS NOT NULL 
BEGIN
    IF OBJECTPROPERTY(OBJECT_ID('dbo.SeatInventory', 'U'), 'TableTemporalType') = 2
        ALTER TABLE dbo.SeatInventory SET (SYSTEM_VERSIONING = OFF);
    DROP TABLE IF EXISTS dbo.SeatInventory_History;
    DROP TABLE dbo.SeatInventory;
END

IF OBJECT_ID('dbo.FarePricing', 'U') IS NOT NULL 
BEGIN
    IF OBJECTPROPERTY(OBJECT_ID('dbo.FarePricing', 'U'), 'TableTemporalType') = 2
        ALTER TABLE dbo.FarePricing SET (SYSTEM_VERSIONING = OFF);
    DROP TABLE IF EXISTS dbo.FarePricing_History;
    DROP TABLE dbo.FarePricing;
END

IF OBJECT_ID('dbo.FlightSchedule', 'U') IS NOT NULL 
BEGIN
    IF OBJECTPROPERTY(OBJECT_ID('dbo.FlightSchedule', 'U'), 'TableTemporalType') = 2
        ALTER TABLE dbo.FlightSchedule SET (SYSTEM_VERSIONING = OFF);
    DROP TABLE IF EXISTS dbo.FlightSchedule_History;
    DROP TABLE dbo.FlightSchedule;
END

DROP TABLE IF EXISTS dbo.Tickets;
DROP TABLE IF EXISTS dbo.Bookings;
DROP TABLE IF EXISTS dbo.Passengers;
DROP TABLE IF EXISTS dbo.Routes;
DROP TABLE IF EXISTS dbo.Aircraft;
DROP TABLE IF EXISTS dbo.Airports;
GO

/* ---------------------------------------------------------
   5.2  Static reference tables
--------------------------------------------------------- */
CREATE TABLE Airports (
    AirportID  INT          IDENTITY PRIMARY KEY,
    IATACode   CHAR(3)      UNIQUE NOT NULL,
    Name       NVARCHAR(60) NOT NULL,
    City       NVARCHAR(40),
    Country    NVARCHAR(40)
);

CREATE TABLE Aircraft (
    AircraftID  INT IDENTITY PRIMARY KEY,
    TailNumber  VARCHAR(10) UNIQUE NOT NULL,
    Model       VARCHAR(30) NOT NULL,
    Seats       INT         NOT NULL
);

CREATE TABLE Routes (
    RouteID     INT IDENTITY PRIMARY KEY,
    OriginID    INT NOT NULL REFERENCES Airports(AirportID),
    DestID      INT NOT NULL REFERENCES Airports(AirportID),
    DistanceKm  INT NOT NULL,
    UNIQUE (OriginID, DestID)
);

CREATE TABLE Passengers (
    PassengerID INT IDENTITY PRIMARY KEY,
    FirstName   NVARCHAR(30),
    LastName    NVARCHAR(30),
    Email       NVARCHAR(100) UNIQUE
);

CREATE TABLE Bookings (
    BookingID   INT IDENTITY PRIMARY KEY,
    PassengerID INT NOT NULL REFERENCES Passengers(PassengerID),
    RouteID     INT NOT NULL REFERENCES Routes(RouteID),
    BookingDate DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE TABLE Tickets (
    TicketID    INT IDENTITY PRIMARY KEY,
    BookingID   INT NOT NULL REFERENCES Bookings(BookingID),
    SeatNumber  VARCHAR(5),
    FarePaid    DECIMAL(10,2)
);

/* ---------------------------------------------------------
   5.3  Temporal tables
--------------------------------------------------------- */

/* 1. FlightSchedule - removed calculated column that referenced DistanceKm */
CREATE TABLE FlightSchedule (
    FlightID        INT IDENTITY PRIMARY KEY,
    RouteID         INT NOT NULL REFERENCES Routes(RouteID),
    AircraftID      INT NOT NULL REFERENCES Aircraft(AircraftID),
    ScheduledDepUTC DATETIME2 NOT NULL,
    ScheduledArrUTC DATETIME2 NOT NULL,  /* Changed to regular column */
    Status          NVARCHAR(20) NOT NULL,
    ValidFrom       DATETIME2 GENERATED ALWAYS AS ROW START,
    ValidTo         DATETIME2 GENERATED ALWAYS AS ROW END,
    PERIOD FOR SYSTEM_TIME (ValidFrom, ValidTo)
)
WITH (SYSTEM_VERSIONING = ON (HISTORY_TABLE = dbo.FlightSchedule_History));

/* 2. FarePricing */
CREATE TABLE FarePricing (
    FareID       INT IDENTITY PRIMARY KEY,
    RouteID      INT NOT NULL REFERENCES Routes(RouteID),
    CabinClass   CHAR(1)  CHECK (CabinClass IN ('Y','J','F')),
    PriceEUR     DECIMAL(10,2) NOT NULL,
    ValidFrom    DATETIME2 GENERATED ALWAYS AS ROW START,
    ValidTo      DATETIME2 GENERATED ALWAYS AS ROW END,
    PERIOD FOR SYSTEM_TIME (ValidFrom, ValidTo),
    UNIQUE (RouteID, CabinClass, ValidTo)
)
WITH (SYSTEM_VERSIONING = ON (HISTORY_TABLE = dbo.FarePricing_History));

/* 3. SeatInventory */
CREATE TABLE SeatInventory (
    FlightID    INT NOT NULL REFERENCES FlightSchedule(FlightID),
    CabinClass  CHAR(1) CHECK (CabinClass IN ('Y','J','F')),
    SeatsLeft   INT NOT NULL CHECK (SeatsLeft >= 0),
    ValidFrom   DATETIME2 GENERATED ALWAYS AS ROW START,
    ValidTo     DATETIME2 GENERATED ALWAYS AS ROW END,
    PERIOD FOR SYSTEM_TIME (ValidFrom, ValidTo),
    CONSTRAINT PK_SeatInventory PRIMARY KEY (FlightID, CabinClass, ValidTo)
)
WITH (SYSTEM_VERSIONING = ON (HISTORY_TABLE = dbo.SeatInventory_History));

/* 4. CrewAssignment */
CREATE TABLE CrewAssignment (
    AssignmentID INT IDENTITY PRIMARY KEY,
    FlightID     INT NOT NULL REFERENCES FlightSchedule(FlightID),
    CrewMember   NVARCHAR(60) NOT NULL,
    Role         NVARCHAR(20),
    ValidFrom    DATETIME2 GENERATED ALWAYS AS ROW START,
    ValidTo      DATETIME2 GENERATED ALWAYS AS ROW END,
    PERIOD FOR SYSTEM_TIME (ValidFrom, ValidTo)
)
WITH (SYSTEM_VERSIONING = ON (HISTORY_TABLE = dbo.CrewAssignment_History));

/* 5. MaintenanceStatus */
CREATE TABLE MaintenanceStatus (
    AircraftID  INT NOT NULL REFERENCES Aircraft(AircraftID),
    Status      NVARCHAR(30) NOT NULL,
    Note        NVARCHAR(200),
    ValidFrom   DATETIME2 GENERATED ALWAYS AS ROW START,
    ValidTo     DATETIME2 GENERATED ALWAYS AS ROW END,
    PERIOD FOR SYSTEM_TIME (ValidFrom, ValidTo),
    CONSTRAINT PK_MaintStatus PRIMARY KEY (AircraftID, ValidTo)
)
WITH (SYSTEM_VERSIONING = ON (HISTORY_TABLE = dbo.MaintenanceStatus_History));
GO

/* ---------------------------------------------------------
   5.4  Temporal rules / constraints
--------------------------------------------------------- */

/* Rule #3: No two FlightSchedules may use the same aircraft at the same time */
CREATE UNIQUE INDEX UX_Aircraft_Uniqueness
ON FlightSchedule (AircraftID, ValidTo);
GO

CREATE TRIGGER TR_SeatInventory_CheckCapacity
ON SeatInventory
AFTER INSERT, UPDATE
AS
BEGIN
    IF EXISTS (
        SELECT 1
        FROM inserted i
        JOIN FlightSchedule fs ON i.FlightID = fs.FlightID
        JOIN Aircraft a ON fs.AircraftID = a.AircraftID
        WHERE i.SeatsLeft > a.Seats
    )
    BEGIN
        ROLLBACK TRANSACTION;
        THROW 50000, 'Seats left cannot exceed aircraft capacity', 1;
    END
END
GO
