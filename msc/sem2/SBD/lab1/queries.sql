USE AirlinesTemporalDB;
GO

DECLARE @Now DATETIME2 = SYSUTCDATETIME();

/* 1. What did Fare Y on Warsaw-Berlin cost recently? (Changed from specific past date) */
SELECT PriceEUR
FROM FarePricing
FOR SYSTEM_TIME AS OF @Now
WHERE RouteID = 1 AND CabinClass='Y';

/* 2. Show full price history for Warsaw-Berlin, newest first */
SELECT PriceEUR, ValidFrom, ValidTo
FROM FarePricing
FOR SYSTEM_TIME ALL
WHERE RouteID = 1
ORDER BY ValidFrom DESC;

/* 3. Which flights were using aircraft SP-LAA between 1–30 June (system time)? */
SELECT FlightID, ScheduledDepUTC
FROM FlightSchedule
FOR SYSTEM_TIME FROM '2024-06-01' TO '2024-06-30'
WHERE AircraftID = 1;

/* 4. Future check – flights for AircraftID 1 scheduled in July 2024 (around its A-check window) */
SELECT F.FlightID, F.ScheduledDepUTC, F.Status
FROM FlightSchedule F
WHERE F.AircraftID = 1
  AND F.ScheduledDepUTC BETWEEN '2024-07-01' AND '2024-07-31'
  AND F.ValidTo = '9999-12-31 23:59:59.9999999';

/* 5. Seat inventory point-in-time: how many Economy seats left right now? */
SELECT SUM(SeatsLeft) AS EconSeatsUnsold
FROM SeatInventory
FOR SYSTEM_TIME AS OF @Now
WHERE CabinClass='Y';

/* 6. Trend – Average Y fare per month (temporal aggregate) */
WITH prices AS (
  SELECT PriceEUR,
         DATEFROMPARTS(YEAR(ValidFrom), MONTH(ValidFrom), 1) AS MonthStart
  FROM FarePricing FOR SYSTEM_TIME ALL
  WHERE CabinClass = 'Y'
)
SELECT MonthStart, AVG(PriceEUR) AS AvgPrice
FROM prices
GROUP BY MonthStart
ORDER BY MonthStart;

/* 7. Which passengers booked flights on routes where the price later increased (from 1st to 2nd version)? */
WITH RoutePriceProgression AS (
    SELECT
        RouteID,
        CabinClass,
        PriceEUR,
        ValidFrom,
        ROW_NUMBER() OVER(PARTITION BY RouteID, CabinClass ORDER BY ValidFrom ASC) as rn
    FROM FarePricing FOR SYSTEM_TIME ALL
    WHERE CabinClass = 'Y'
),
RoutesWithIncreaseFromFirstToSecond AS (
    SELECT P1.RouteID
    FROM RoutePriceProgression P1
    JOIN RoutePriceProgression P2 ON P1.RouteID = P2.RouteID AND P1.CabinClass = P2.CabinClass
    WHERE P1.rn = 1 AND P2.rn = 2 AND P2.PriceEUR > P1.PriceEUR
)
SELECT DISTINCT P.FirstName, P.LastName
FROM Passengers P
JOIN Bookings B ON P.PassengerID = B.PassengerID
WHERE B.RouteID IN (SELECT RouteID FROM RoutesWithIncreaseFromFirstToSecond);

/* 8. Past seat availability vs. now – detect high-selling flights */
WITH InitialSeatInventory AS (
    SELECT
        FlightID,
        CabinClass,
        SeatsLeft,
        ROW_NUMBER() OVER(PARTITION BY FlightID, CabinClass ORDER BY ValidFrom ASC) as rn
    FROM SeatInventory FOR SYSTEM_TIME ALL
    WHERE CabinClass = 'Y'
)
SELECT
    F.FlightID,
    ISI.SeatsLeft AS SeatsInitially,
    SI_current.SeatsLeft AS SeatsNow,
    (COALESCE(ISI.SeatsLeft, 0) - COALESCE(SI_current.SeatsLeft, 0)) AS SeatsSold
FROM FlightSchedule F
JOIN InitialSeatInventory ISI
    ON F.FlightID = ISI.FlightID AND ISI.CabinClass = 'Y' AND ISI.rn = 1
JOIN SeatInventory SI_current
    ON SI_current.FlightID = F.FlightID AND SI_current.CabinClass = 'Y'
    AND SI_current.ValidTo = '9999-12-31 23:59:59.9999999'
WHERE F.ValidTo = '9999-12-31 23:59:59.9999999'
ORDER BY SeatsSold DESC;

/* 9. Timeline of maintenance states for aircraft 1 */
SELECT Status, Note, ValidFrom, ValidTo
FROM MaintenanceStatus
FOR SYSTEM_TIME ALL
WHERE AircraftID = 1
ORDER BY ValidFrom;

/* 10. "What-if" – Which flights for Aircraft 1 conflict with its scheduled A-check period (July 10-20, 2024)? */
DECLARE @AcheckStartAppTime DATETIME2 = '2024-07-10 00:00:00';
DECLARE @AcheckEndAppTime DATETIME2 = '2024-07-20 00:00:00';

SELECT F.FlightID, F.ScheduledDepUTC, F.Status
FROM FlightSchedule F
WHERE F.AircraftID = 1
  AND F.ScheduledDepUTC >= @AcheckStartAppTime
  AND F.ScheduledDepUTC < @AcheckEndAppTime
  AND F.ValidTo = '9999-12-31 23:59:59.9999999';

/* 11. Aircraft recorded as 'In Maintenance' during a recent application period (e.g., last day) */
DECLARE @RecentAppPeriodStart DATETIME2 = DATEADD(day, -1, @Now);
DECLARE @RecentAppPeriodEnd DATETIME2 = @Now;

SELECT DISTINCT AC.TailNumber, M.Status, M.Note, M.ValidFrom AS StatusValidFrom_Sys, M.ValidTo AS StatusValidTo_Sys
FROM MaintenanceStatus FOR SYSTEM_TIME ALL M
JOIN Aircraft AC ON M.AircraftID = AC.AircraftID
WHERE M.Status = 'In Maintenance'
  AND M.ValidFrom < @RecentAppPeriodEnd
  AND M.ValidTo > @RecentAppPeriodStart;
