USE AirlinesTemporalDB;
GO

DECLARE @Now DATETIME2 = SYSUTCDATETIME();

/* 1. What did Fare Y on Warsaw-Berlin cost on 1 May 2024 ? */
SELECT PriceEUR
FROM FarePricing
FOR SYSTEM_TIME AS OF '2024-05-01'
WHERE RouteID = 1 AND CabinClass='Y';

/* 2. Show full price history for Warsaw-Berlin, newest first */
SELECT PriceEUR, ValidFrom, ValidTo
FROM FarePricing
FOR SYSTEM_TIME ALL
WHERE RouteID = 1
ORDER BY ValidFrom DESC;

/* 3. Which flights were using aircraft SP-LAA between 1–30 June? */
SELECT FlightID, ScheduledDepUTC
FROM FlightSchedule
FOR SYSTEM_TIME FROM '2024-06-01' TO '2024-06-30'
WHERE AircraftID = 1;

/* 4. Future check – flights for AircraftID 1 scheduled (application time) after its A-check window */
SELECT F.FlightID, F.ScheduledDepUTC, F.Status
FROM FlightSchedule F
WHERE F.AircraftID = 1
  AND F.ScheduledDepUTC > '2024-07-20'
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

/* 7. Which passengers booked flights whose price later increased? */
WITH FareAtBookingTime AS (
    SELECT
        B.BookingID,
        B.PassengerID,
        FP_Hist.PriceEUR,
        B.RouteID,
        'Y' AS CabinClass
    FROM Bookings B
    JOIN FarePricing FOR SYSTEM_TIME ALL FP_Hist
      ON B.RouteID = FP_Hist.RouteID AND FP_Hist.CabinClass = 'Y'
    WHERE B.BookingDate >= FP_Hist.ValidFrom AND B.BookingDate < FP_Hist.ValidTo
),
CurrentFares AS (
    SELECT RouteID, CabinClass, PriceEUR
    FROM FarePricing
    FOR SYSTEM_TIME AS OF @Now
    WHERE CabinClass = 'Y'
)
SELECT DISTINCT P.FirstName, P.LastName
FROM Passengers P
JOIN FareAtBookingTime FAB ON P.PassengerID = FAB.PassengerID
WHERE EXISTS (
    SELECT 1
    FROM CurrentFares CF
    WHERE CF.RouteID = FAB.RouteID
      AND CF.CabinClass = FAB.CabinClass
      AND CF.PriceEUR > FAB.PriceEUR
);

/* 8. Past seat availability vs. now – detect high-selling flights */
-- Revised to find the earliest inventory record more reliably
WITH InitialSeatInventory AS (
    SELECT
        FlightID,
        CabinClass,
        SeatsLeft,
        -- Assign row number 1 to the earliest record for each flight/class
        ROW_NUMBER() OVER(PARTITION BY FlightID, CabinClass ORDER BY ValidFrom ASC) as rn
    FROM SeatInventory FOR SYSTEM_TIME ALL
    WHERE CabinClass = 'Y'
)
SELECT
    F.FlightID,
    ISI.SeatsLeft AS SeatsInitially,
    SI_current.SeatsLeft AS SeatsNow,
    -- Calculate seats sold based on the earliest known inventory and current inventory
    (COALESCE(ISI.SeatsLeft, 0) - COALESCE(SI_current.SeatsLeft, 0)) AS SeatsSold
FROM FlightSchedule F
-- Join with the earliest inventory record (rn=1)
JOIN InitialSeatInventory ISI
    ON F.FlightID = ISI.FlightID AND ISI.CabinClass = 'Y' AND ISI.rn = 1
-- Join with the current inventory record
JOIN SeatInventory SI_current
    ON SI_current.FlightID = F.FlightID AND SI_current.CabinClass = 'Y'
    AND SI_current.ValidTo = '9999-12-31 23:59:59.9999999'
-- Consider only currently valid flight schedules
WHERE F.ValidTo = '9999-12-31 23:59:59.9999999'
ORDER BY SeatsSold DESC;

/* 9. Timeline of maintenance states for aircraft 1 */
SELECT Status, Note, ValidFrom, ValidTo
FROM MaintenanceStatus
FOR SYSTEM_TIME ALL
WHERE AircraftID = 1
ORDER BY ValidFrom;

/* 10. "What-if" – Which flights overlap with any 'Unserviceable' period of Aircraft 1? */
WITH Aircraft1Maintenance AS (
    SELECT Status, Note, ValidFrom, ValidTo
    FROM MaintenanceStatus FOR SYSTEM_TIME ALL
    WHERE AircraftID = 1 AND Status = 'Scheduled A-check' AND Note = 'Aircraft unavailable'
)
SELECT F.FlightID, F.ScheduledDepUTC, M.Status AS MaintenanceStatusAtTimeOfCheck, M.ValidFrom AS MaintRecord_ValidFrom, M.ValidTo AS MaintRecord_ValidTo
FROM FlightSchedule F
CROSS JOIN Aircraft1Maintenance M
WHERE F.AircraftID = 1
  AND F.ScheduledDepUTC >= M.ValidFrom
  AND F.ScheduledDepUTC < M.ValidTo
  AND F.ValidTo = '9999-12-31 23:59:59.9999999';

/* 11. Aircraft recorded as 'In Maintenance' during a specific application period */
DECLARE @AppPeriodStart DATETIME2 = '2025-05-11 15:01:43.0000000';
DECLARE @AppPeriodEnd DATETIME2 = '2025-05-11 15:01:45.0000000';

SELECT DISTINCT AC.TailNumber, M.Status, M.Note, M.ValidFrom AS StatusValidFrom, M.ValidTo AS StatusValidTo
FROM MaintenanceStatus FOR SYSTEM_TIME ALL M
JOIN Aircraft AC ON M.AircraftID = AC.AircraftID
WHERE M.Status = 'In Maintenance'
  AND M.ValidFrom < @AppPeriodEnd
  AND M.ValidTo > @AppPeriodStart;
