use UbermetricsMigration

-- MATCH UBERMETRICS 
SELECT T.*, 100 * T.[JSON feeds found in UB] / T.[# JSON feeds] as '% JSON feeds found in UB'
FROM (
	SELECT
	  (SELECT count(DISTINCT json_file_path) FROM [matchings.all]) as '# JSON files' 
	, (SELECT COUNT(DISTINCT json_feed_id) FROM [matchings.all]) as '# JSON feeds'
	, (SELECT COUNT(DISTINCT json_feed_id) FROM [dbo].[matchings.all] WHERE ub_login IS NOT NULL) as 'JSON feeds found in UB' 
) as T 

-- FACTORY 
SELECT T.*, 100 * T.[# FACTORY feeds FOUND in JSON feeds] / T.[# FACTORY feeds] as '% FACTORY feeds found in JSON',  100 * T.[# FACTORY feeds FOUND in UB] / T.[# FACTORY feeds] as '% FACTORY feeds found in UB'
FROM (	
	SELECT
	  (SELECT COUNT(DISTINCT Customer_ID) FROM factory_feeds) as '# FACTORY feeds' 
	, (SELECT COUNT(DISTINCT ff.Customer_ID) FROM factory_feeds ff LEFT JOIN [matchings.all] jf ON ff.[Monitor_Key]=jf.[json_feed_key] WHERE jf.json_feed_id is not null) as '# FACTORY feeds found in JSON feeds' 
	, (SELECT COUNT(DISTINCT ff.Customer_ID) FROM factory_feeds ff 
			LEFT JOIN [matchings.all] ON ff.[Monitor_Key]=[json_feed_key] 
		WHERE ub_login is not null
	) as '# FACTORY feeds found in UB' 
) as T

-- NEWSLETTERS 
SELECT 
	(SELECT count(distinct CAST(idCustomer as nvarchar(20)) + newsletter_id) FROM [UbermetricsMigration].[dbo].[json_newsletters]) as '# NEWSLETTERS'
	,(SELECT count(distinct CAST(nl.idCustomer as nvarchar(20)) + newsletter_id) FROM [UbermetricsMigration].[dbo].[json_newsletters] nl INNER JOIN [matchings.all] ma ON ma.json_feed_id= nl.feed_id) as '# NEWSLETTERS actives'
	
-- FEEDS NEWSLETTERS 
SELECT T.*, 100 * T.[# NEWSLETTERS feeds FOUND in UB] / T.[# NEWSLETTERS feeds] as '% NEWSLETTERS found in UB'
FROM (
	SELECT 
		(SELECT COUNT(DISTINCT nl.feed_id) FROM json_newsletters nl INNER JOIN [matchings.all] ub ON ub.json_feed_id=nl.feed_id) as '# NEWSLETTERS feeds'
		, (SELECT COUNT(DISTINCT nl.feed_id) FROM json_newsletters nl INNER JOIN [dbo].[matchings.all] ub ON nl.feed_id = ub.json_feed_id INNER JOIN factory_feeds ff ON ub.json_feed_key = ff.Monitor_Key) as '# NEWSLETTERS feeds found in Factory'
		, (SELECT COUNT(DISTINCT jnl.feed_id) FROM json_newsletters jnl INNER JOIN [matchings.all] ma ON jnl.feed_id=ma.json_feed_id WHERE ub_login IS NOT NULL) as '# NEWSLETTERS feeds found in UB'
) AS T

-- Repartition par folder
SELECT T.* 
FROM (
	SELECT folder_name as 'customers', 
		count(ub_login) as 'nb_searches_found', 
		count(folder_name)-count(ub_login) as 'nb_searches_not_found', 
		count(folder_name) as 'nb_feeds_total', 
		count(ub_login) * 100 / count(folder_name) as 'percent'
	FROM [UbermetricsMigration].[dbo].[matchings.all] 
	GROUP BY folder_name
) AS T
ORDER BY T.[percent] DESC, T.[customers] ASC


