USE AirlinesTemporalDB;
GO

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

/* 4. Future check – flights after the scheduled maintenance window */
SELECT FlightID, ScheduledDepUTC
FROM FlightSchedule
WHERE AircraftID = 1
  AND ScheduledDepUTC BETWEEN '2024-07-10' AND '2024-07-20';

/* 5. Seat inventory point-in-time: how many Economy seats left right now? */
SELECT SUM(SeatsLeft) AS EconSeatsUnsold
FROM SeatInventory
FOR SYSTEM_TIME AS OF SYSUTCDATETIME()
WHERE CabinClass='Y';

/* 6. Trend – Average Y fare per month (temporal aggregate) */
WITH prices AS (
  SELECT PriceEUR,
         DATEFROMPARTS(YEAR(ValidFrom), MONTH(ValidFrom), 1) AS MonthStart
  FROM FarePricing FOR SYSTEM_TIME ALL
)
SELECT MonthStart, AVG(PriceEUR) AS AvgPrice
FROM prices
GROUP BY MonthStart
ORDER BY MonthStart;

/* 7. Which passengers booked flights whose price later increased? */
SELECT DISTINCT P.FirstName, P.LastName
FROM Passengers P
JOIN Bookings   B ON P.PassengerID=B.PassengerID
JOIN Routes     R ON B.RouteID = R.RouteID
JOIN FarePricing FP
     FOR SYSTEM_TIME FROM B.BookingDate TO B.BookingDate
       ON FP.RouteID = R.RouteID AND FP.CabinClass='Y'
WHERE EXISTS(
   SELECT 1 FROM FarePricing FP2
   FOR SYSTEM_TIME AS OF SYSUTCDATETIME()
   WHERE FP2.RouteID=FP.RouteID AND FP2.CabinClass='Y'
     AND FP2.PriceEUR > FP.PriceEUR);

/* 8. Past seat availability vs. now – detect high-selling flights */
SELECT F.FlightID,
       SI0.SeatsLeft      AS SeatsInitially,
       SIcurr.SeatsLeft   AS SeatsNow,
       SI0.SeatsLeft - SIcurr.SeatsLeft AS SeatsSold
FROM FlightSchedule F
JOIN SeatInventory SI0   FOR SYSTEM_TIME AS OF F.ValidFrom
     ON SI0.FlightID = F.FlightID
JOIN SeatInventory SIcurr
     ON SIcurr.FlightID = F.FlightID
ORDER BY SeatsSold DESC;

/* 9. Timeline of maintenance states for aircraft 1 */
SELECT Status, Note, ValidFrom, ValidTo
FROM MaintenanceStatus
FOR SYSTEM_TIME ALL
WHERE AircraftID = 1
ORDER BY ValidFrom;

/* 10. “What-if” – Which flights overlap with any ‘Unserviceable’ period? */
SELECT F.FlightID, F.ScheduledDepUTC
FROM FlightSchedule F
JOIN MaintenanceStatus M FOR SYSTEM_TIME ALL
  ON F.AircraftID = M.AircraftID
WHERE M.Status LIKE 'Unserviceable%'
  AND F.ScheduledDepUTC BETWEEN M.ValidFrom AND M.ValidTo;
