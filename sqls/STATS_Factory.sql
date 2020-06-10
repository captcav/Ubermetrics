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
		AND C.Customer_Name not like ('Imente_DKV_%')
		AND C.Customer_Name not like ('Augure_Pandora_%')
		AND C.Customer_Name not like ('Augure_GStarRAW_%')
		AND C.Customer_Name not like ('Imente_MRA_Glashutte%')
		AND C.Customer_Name not like ('Imente_Artelier_Frinsa%')
		AND C.Customer_Name not like ('Augure_SC_SerenaCapital%')
		AND (CF.Source_Path not like '%TNUMwYVhbpHyC1499hLHg%' AND CF.Source_Path not like '%89OUIOT1aNoiaOzgwc3Z3.%' AND CF.Source_Path not like '%hUMGarN5saOGVMdY0nFBl%' AND CF.Source_Path not like '%qqmZ45uOR6PKMn6A8bjCl%' AND CF.Source_Path not like '%8.IiIU0QnNtiwkkyJmnsz%' AND CF.Source_Path not like '%vMPdTxFkHFk33OtRyZiO1%' AND CF.Source_Path not like '%VcpTfxgmjLWDLtx1ET3W31%' AND CF.Source_Path not like '%P5CGVMY6ttVr9TsbetXN4%' AND CF.Source_Path not like '%1S31uLsX1M44P8ubj8Sfj0%' AND CF.Source_Path not like '%4nQGMTr4Jn4DJAUBEczVl.%') --exclude Imente_MRA
		AND (CF.Source_Path not like '%Km2JJoZLO6ZKX8DNCh53I1%' AND CF.Source_Path not like '%G9eVA5cFUc3fYcX5wcC9Q1%' AND CF.Source_Path not like '%1lIsVO.Njk5z8hLg2EbVv0%' AND CF.Source_Path not like '%adb0nEeCcD0d8aPscl6tF0%' AND CF.Source_Path not like '%P6XmeoV2PSg27Mz1xkmjU0%' AND CF.Source_Path not like '%Rs4RWTqKCVVW8xX3Ocq40%' AND CF.Source_Path not like '%02f3FKpgQG0AArsAR7Tmv1%' AND CF.Source_Path not like '%W5DYza6TcoEu.sX2y1NbX.%' AND CF.Source_Path not like '%Zx7GtSDHm3NF5swoQudL7.%' AND CF.Source_Path not like '%JL9n2gCILnefWsYMDKyU0%' AND CF.Source_Path not like '%rnTE9UAjvm1yiH1.AYPl.0%' AND CF.Source_Path not like '%Hol.nCIM9.WAG8w.GInuF%' AND CF.Source_Path not like '%3.4manlLkmtij.rAWjURj.%' AND CF.Source_Path not like '%kxdKm4Tbi8gr9dw5nGgih0%') -- exclude DEVA
		AND (CF.Source_Path not like '%FKPgzH02kfpjns9H2Jlt%' AND CF.Source_Path not like '%IfgLR3ZKSWlSuFLXzLqUx%' AND CF.Source_Path not like '%sPV7TObGsjtzk20bmrdo%' AND CF.Source_Path not like  '%41lEOrySl6piCQY5dUiYU%') -- exclude Respol
		AND (CF.Source_Path not like '%WWlJsLSAqR1DVmRbRh.GT.%' AND CF.Source_Path not like '%88Cbc2FVgKX662TqNatd.%' AND CF.Source_Path not like '%DcoEWKOXIR6YXoFDznQt%') --exclude Endesa
) AS T 
ORDER BY T.Customer_Name

-- Nb articles.
SELECT COUNT(*) as 'nb_articles_total' FROM [dbo].[SOURCE_CLIPS] clip

-- Nb articles per day.
SELECT 	CONVERT(varchar, [Process_Date], 111) as process_date, 
		COUNT(Source_Clips_ID) as 'nb_articles'
FROM [UberFactory].[dbo].[SOURCE_CLIPS] 
GROUP BY CONVERT(varchar, [Process_Date], 111) 
ORDER BY CONVERT(varchar, [Process_Date], 111) ASC

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
