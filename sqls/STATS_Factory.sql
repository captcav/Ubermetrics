USE Factory

-- Active Monitor feeds in the Factory
SELECT T.*
, LEFT(SUBSTRING(T.Source_Path, CHARINDEX('clau=', T.Source_Path)+5, 100), CHARINDEX('&', SUBSTRING(T.Source_Path, CHARINDEX('clau=', T.Source_Path)+5, 100))-1) as Monitor_Key
FROM (
	SELECT CF.Customer_ID
	, C.Customer_Name
	, C.Destination_Path
	, P.ProviderFTP
	, REPLACE(REPLACE(CF.Source_Path,'ecode.cgi?', 'ccode.cgi?clau='),'ccode.cgi?lvRd2VAkWbwbtXG8QwKK','ccode.cgi?clau=lvRd2VAkWbwbtXG8QwKK') + '&' as Source_Path
	, C.ApplicationUrl
	, CASE 
		WHEN ApplicationURL IS NULL OR LEN(ApplicationUrl)=0 THEN SUBSTRING(Customer_Name,1, CHARINDEX('_', Customer_Name, 8) - 1)
		ELSE SUBSTRING(ApplicationUrl, CHARINDEX('/', ApplicationUrl,10) +1, 100)
	END as 'ApplicationName'
	FROM [Factory].[dbo].[CUSTOMER_FILE_DETAILS] CF
		 INNER JOIN SCHEDULE S ON S.Customer_ID=CF.Customer_ID
		 INNER JOIN CUSTOMERS C ON C.Customer_ID=CF.Customer_ID
		 INNER JOIN [PROVIDER] P ON P.Provider_ID = C.Provider_Id
	 WHERE C.Provider_Id in (261, 481)  AND S.Schedule_Status=1
) AS T 

SELECT count(*) as nb_pige_total 
FROM [dbo].[SOURCE_CLIPS] clip
		INNER JOIN CUSTOMERS C ON C.Customer_ID=clip.Customer_ID
		INNER JOIN SCHEDULE S ON S.Customer_ID=C.Customer_ID
WHERE clip.Provider_ID in (261,481) AND S.Schedule_Status=1

SELECT C.Customer_Name 
	, CF.Source_Path
	, YEAR(clip.[Process_Date]) as [year]
	, MONTH(clip.[Process_Date]) as [month]
	, COUNT(*) as nb_pige_per_feed
FROM [dbo].[SOURCE_CLIPS] clip
		INNER JOIN CUSTOMERS C ON C.Customer_ID=clip.Customer_ID
		INNER JOIN [CUSTOMER_FILE_DETAILS] CF ON C.Customer_ID=CF.Customer_ID
		INNER JOIN SCHEDULE S ON S.Customer_ID=C.Customer_ID
WHERE clip.Provider_ID in (261,481) AND S.Schedule_Status=1
GROUP BY C.Customer_Name, CF.Source_Path, YEAR(clip.Process_Date), MONTH(clip.Process_Date)
ORDER BY C.Customer_Name, CF.Source_Path, YEAR(clip.[Process_Date]), MONTH(clip.[Process_Date])

-- # Monitor clips processed by the Factory
SELECT YEAR(clip.[Process_Date]) as [year]
	, MONTH(clip.[Process_Date]) as [month]
	, COUNT(*) as [nb_piges]
	, COUNT(DISTINCT S.Schedule_ID) as [nb_feeds]
	, COUNT(*) / COUNT(DISTINCT S.Schedule_ID) as [nb_piges_per_feed]
FROM [dbo].[SOURCE_CLIPS] clip
	INNER JOIN CUSTOMERS C ON C.Customer_ID=clip.Customer_ID
	INNER JOIN SCHEDULE S ON S.Customer_ID=C.Customer_ID
WHERE clip.Provider_ID in (261,481) AND S.Schedule_Status=1
AND MONTH(clip.Process_Date) not in (MONTH(GETDATE()))
GROUP BY YEAR(clip.Process_Date), MONTH(clip.Process_Date)
ORDER BY YEAR(clip.Process_Date) DESC, MONTH(clip.Process_Date) DESC

SELECT AVG(ALL T.[nb_piges]) as [average_piges_per_month] 
	, AVG(ALL T.[nb_feeds]) as [average_feeds_per_month] 
	, AVG(ALL T.[nb_piges_per_feed]) as [average_piges_per_feed_per_month] 
FROM (
	SELECT YEAR(clip.[Process_Date]) as [year]
		, MONTH(clip.[Process_Date]) as [month]
		, COUNT(*) as [nb_piges]
		, COUNT(DISTINCT S.Schedule_ID) as [nb_feeds]
		, COUNT(*) / COUNT(DISTINCT S.Schedule_ID) as [nb_piges_per_feed]
	FROM [dbo].[SOURCE_CLIPS] clip
		INNER JOIN CUSTOMERS C ON C.Customer_ID=clip.Customer_ID
		INNER JOIN SCHEDULE S ON S.Customer_ID=C.Customer_ID
	WHERE clip.Provider_ID in (261,481) AND S.Schedule_Status=1
	AND MONTH(clip.Process_Date) not in (MONTH(GETDATE()))
	GROUP BY YEAR(clip.Process_Date), MONTH(clip.Process_Date)
) AS T
