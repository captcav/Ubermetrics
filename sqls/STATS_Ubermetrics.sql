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
SELECT T.*
, T.[# FACTORY feeds] - T.[# FACTORY feeds found in JSON feeds] as '# FACTORY feeds missing in JSON'
, T.[# FACTORY feeds found in JSON feeds] - T.[# FACTORY feeds found in UB] as '# FACTORY feeds that are well defined in JSON but missing in UM'
--, 100 * T.[# FACTORY feeds FOUND in JSON feeds] / T.[# FACTORY feeds] as '% FACTORY feeds found in JSON'
--, 100 * T.[# FACTORY feeds FOUND in UB] / T.[# FACTORY feeds found in JSON feeds]	 as '% FACTORY feeds found in UB'
FROM (	
	SELECT
	  (SELECT COUNT(DISTINCT ff.Monitor_Key) FROM factory_feeds ff) as '# FACTORY feeds' 
	, (SELECT COUNT(DISTINCT ff.Monitor_key) FROM factory_feeds ff LEFT JOIN [matchings.all] jf ON ff.[Monitor_Key]=jf.[json_feed_key] WHERE jf.json_feed_id is not null) as '# FACTORY feeds found in JSON feeds' 
	, (SELECT COUNT(DISTINCT ff.Monitor_key) FROM factory_feeds ff LEFT JOIN [matchings.all] ON ff.[Monitor_Key]=[json_feed_key] WHERE ub_login is not null and json_feed_key IS NOT NULL) as '# FACTORY feeds found in UB' 
) as T

-- Missing JSON Factory's feeds definition.
/*
SELECT DISTINCT ff.Customer_Name, ff.Source_Path as 'feed_url', ff.Monitor_Key, ff.ProviderFTP + ff.Source_Path as 'feed_url', ff.ApplicationName, ma.json_feed_key
FROM factory_feeds ff
	LEFT JOIN [matchings.all] ma ON ff.[Monitor_Key]=ma.[json_feed_key] 
WHERE ma.json_feed_key IS NULL 
ORDER BY ff.ApplicationName, ff.Customer_Name

-- Well JSON defined Factory's feeds missing in the UM platform.
SELECT DISTINCT ma.json_file_path, ma.json_customer_id, ma.json_customer_name, ma.json_feed_id, ma.json_feed_name
FROM factory_feeds ff
	LEFT JOIN [matchings.all] ma ON ff.[Monitor_Key]=ma.[json_feed_key] 
WHERE ma.ub_login IS  NULL
AND ma.json_feed_key IS NOT NULL
ORDER BY ma.json_file_path
*/

-- NEWSLETTERS 
SELECT 
	(SELECT count(distinct file_path + CAST(idCustomer as nvarchar(20)) + newsletter_id) FROM [UbermetricsMigration].[dbo].[json_newsletters]) as '# NEWSLETTERS'
	,(SELECT count(distinct file_path + CAST(nl.idCustomer as nvarchar(20)) + newsletter_id) FROM [UbermetricsMigration].[dbo].[json_newsletters] nl INNER JOIN [matchings.all] ma ON ma.json_feed_id= nl.feed_id) as '# NEWSLETTERS actives'
	
-- FEEDS NEWSLETTERS 
SELECT T.*
--, 100 * T.[# NEWSLETTERS feeds FOUND in UB] / T.[# NEWSLETTERS feeds] as '% NEWSLETTERS found in UB'
FROM (
	SELECT 
		(SELECT COUNT(DISTINCT nl.feed_id) FROM json_newsletters nl INNER JOIN [matchings.all] ub ON ub.json_feed_id=nl.feed_id) as '# NEWSLETTERS feeds'
		, (SELECT COUNT(DISTINCT nl.feed_id) FROM json_newsletters nl INNER JOIN [dbo].[matchings.all] ub ON nl.feed_id = ub.json_feed_id INNER JOIN factory_feeds ff ON ub.json_feed_key = ff.Monitor_Key) as '# NEWSLETTERS feeds found in Factory'
		, (SELECT COUNT(DISTINCT jnl.feed_id) FROM json_newsletters jnl INNER JOIN [matchings.all] ma ON jnl.feed_id=ma.json_feed_id WHERE ub_login IS NOT NULL) as '# NEWSLETTERS feeds found in UB'
		, (SELECT Count(*) FROM (
				SELECT distinct T.idCustomer, T.file_path, T.newsletter_id , T.feed_id
				FROM (
					SELECT distinct nl.idCustomer, nl.file_path, nl.newsletter_id , nl.feed_id, ma.json_feed_id
					FROM [UbermetricsMigration].[dbo].[json_newsletters] nl 
						LEFT JOIN [matchings.all] ma ON ma.json_feed_id= nl.feed_id
				--	ORDER BY ma.json_feed_id, nl.file_path, nl.newsletter_id
				) AS T
				WHERE T.json_feed_id IS NULL) 
			AS U) AS '# NEWSLETTERS with missing feeds'
) AS T

-- Newsletter's feeds missing in the UM platform.
/*
SELECT DISTINCT ma.json_file_path, ma.json_customer_id, ma.json_customer_name, ma.json_feed_id, ma.json_feed_name
FROM json_newsletters jnl 
	INNER JOIN [matchings.all] ma ON jnl.feed_id=ma.json_feed_id WHERE ub_login IS NULL
*/		
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


