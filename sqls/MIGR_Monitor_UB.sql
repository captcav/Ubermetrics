use UbermetricsMigration

DECLARE @NEXT_INTEGRATION_PARAMETER as nvarchar(10) = '637371072000000000' -- http://www.datetimetoticks-converter.com/
DECLARE @SCHEDULE_START_DATE as nvarchar(10) = (SELECT CAST(CONVERT(date,GETDATE()) AS nvarchar(10)))
DECLARE @SCHEDULE_STATUS as bit = 0

DECLARE @destination_path_base as nvarchar(255) = 'https://data.hosting.augure.com/uberfactory'
DECLARE @sql as nvarchar(max) = ''
DECLARE @counter_done as int = 0
DECLARE @counter_not_done as int = 0

PRINT 'USE UberFactory'
PRINT 'BEGIN TRAN' 

-- CREATE A NEW PROVIDER UBERMETRICS  --
PRINT 'DECLARE @ProviderID as int;'

DECLARE @provider_name as nvarchar(255) = 'Ubermetrics'
SET @sql = 'IF NOT EXISTS(SELECT 1 FROM PROVIDER WHERE Provider_Name=''' + @provider_name + ''') '
SET @sql = @sql + 'INSERT INTO [dbo].[PROVIDER] ([Provider_Name],[Provider_Status],[Provider_Type],[Provider_Transform_Filename],[IsFileDeleted],[DownloadLimitInDays],[IsDedicatedWatcherNeeded]) '
SET @sql = @sql + 'VALUES ('''+ @provider_name + ''',1,''REST'',''UBERMETRICS'',0,0,0);'
SET @sql = @sql + 'SET @ProviderID=(SELECT Provider_ID FROM PROVIDER WHERE Provider_Name=''' + @provider_name + ''');'

PRINT @sql

PRINT ''
PRINT '------------------------------------------------------------'
PRINT '-- INFO - 1 new provider created'
PRINT '------------------------------------------------------------'
PRINT ''

-- CREATE CUSTOMERS --
DECLARE @ub_login as nvarchar(255)
DECLARE @ub_password as nvarchar(255)
DECLARE @factory_customer_id as nvarchar(255)
DECLARE @factory_customer_name as nvarchar(255)
DECLARE @factory_destination_path as nvarchar(255)	
DECLARE @factory_monitor_key as nvarchar(255)
DECLARE @destination_path AS nvarchar(500)
DECLARE @factory_application_url as nvarchar(500)
DECLARE @application_url as nvarchar(500)
DECLARE @json_customer_id as nvarchar(255)
DECLARE @json_customer_name as nvarchar(255)	
DECLARE @json_customer_name_normalized as nvarchar(255)	
DECLARE @json_feed_id as nvarchar(255)
DECLARE @json_feed_name as nvarchar(255)
DECLARE @json_feed_name_normalized as nvarchar(255)
DECLARE @ub_folder_id as nvarchar(255)

DECLARE customer_cursor CURSOR FOR
SELECT DISTINCT  ff.Customer_ID, ff.Customer_Name, ff.Destination_Path 
, CASE 
	WHEN ff.ApplicationUrl IS NOT NULL AND LEN(ff.ApplicationUrl) > 0 THEN ff.ApplicationUrl
	WHEN acc.[app_url] = '???' OR acc.[app_url] IS NULL OR LEN(acc.[app_url])=0 THEN aa.[url]
	ELSE acc.[app_url]
END as 'url_selected'
, ub.json_customer_id, ub.json_customer_name, ub.[json_customer_name_normalized], ub.json_feed_id, ub.json_feed_name, ub.[json_feed_name_normalized], ub.ub_login, ub.ub_password, ub.ub_name, ff.Monitor_Key
FROM factory_feeds ff
	LEFT JOIN [dbo].[matchings.all] ub ON ff.Monitor_Key = ub.json_feed_key
	LEFT JOIN [ub.accounts] acc ON acc.login = ub.ub_login
	LEFT JOIN [augure.apps] aa ON aa.url LIKE '%' + ff.ApplicationName
ORDER BY ub_login, json_customer_id, json_feed_id

OPEN customer_cursor
FETCH NEXT FROM customer_cursor INTO @factory_customer_id, @factory_customer_name, @factory_destination_path, @factory_application_url, @json_customer_id, @json_customer_name, @json_customer_name_normalized, @json_feed_id, @json_feed_name, @json_feed_name_normalized, @ub_login, @ub_password, @ub_folder_id, @factory_monitor_key

PRINT 'DECLARE @newCustomerID as int;'
PRINT 'DECLARE @old_schedule_id as int;'
PRINT 'IF NOT EXISTS (select * from dbo.sysobjects where id = object_id(N''[dbo].[ub_new_customers]'')) '
PRINT 'CREATE TABLE dbo.[ub_new_customers] ([monitor_feed_id] int NOT NULL, [monitor_feed_name] nvarchar(500) NULL, [monitor_customer_id] int NOT NULL, [monitor_customer_name] nvarchar(100) NOT NULL, [new_customer_id] int NOT NULL, [new_provider_id] int NOT NULL, [old_customer_id] int NULL, [type] nvarchar(20) NOT NULL, [new_destination_path] nvarchar(500) NOT NULL, [old_destination_path] nvarchar(500) NULL, [augure_application] nvarchar(500) NULL, ub_login nvarchar(100) NOT NULL, ub_search_id int NOT NULL); '
PRINT 'TRUNCATE TABLE dbo.[ub_new_customers];'
PRINT 'IF NOT EXISTS (select * from dbo.sysobjects where id = object_id(N''[dbo].[ub_new_schedules]'')) '
PRINT 'CREATE TABLE dbo.[ub_new_schedules] ([new_schedule_id] int NOT NULL, [new_customer_id] int NULL, [old_schedule_id] int NULL, [old_customer_id] int NULL) '
PRINT 'TRUNCATE TABLE dbo.[ub_new_schedules];'

SET @counter_done = 0
SET @counter_not_done = 0
WHILE @@FETCH_STATUS = 0  
BEGIN 
	IF @ub_folder_id IS NOT NULL 
	BEGIN 
		DECLARE @normalizedCustomerFolderName as nvarchar(500) = @provider_name + '_' + REPLACE(@ub_login,'-Augure-API','') + '_' +  @json_customer_name_normalized + @json_feed_name_normalized
		DECLARE @ub_api as nvarchar(500) = '/v2/mentions?searches.id=' + cast(@ub_folder_id as nvarchar(20)) + '&document.published.geq={0}' --&highlights=true&highlightTag=b'
		SET @destination_path= @destination_path_base + '/' + @normalizedCustomerFolderName + '/feed.xml'

		-- Table CUSTOMERS
		SET @sql = 'INSERT INTO CUSTOMERS (Customer_Name, SourceConnectionProtocol, SourceConnectionUrl, SourceConnectionUsername , SourceConnectionPassword, Destination_Path, FeedVersion, FeedClipDays, Customer_Status, ApplicationUrl, Provider_Id) '
		SET @sql = @sql + 'OUTPUT ' + @json_feed_id + ',''' + REPLACE(@json_feed_name, '''','') + ''',' + CAST(@json_customer_id as nvarchar(20)) + ',''' + @json_customer_name_normalized + ''', INSERTED.Customer_ID, @ProviderID, ' + CAST(@factory_customer_id AS nvarchar(20)) + ', ''factory'', ''' + @destination_path + ''',''' + @factory_destination_path + ''',''' + @factory_application_url + ''',''' + @ub_login + ''',''' + @ub_folder_id + ''' INTO ub_new_customers (monitor_feed_id, monitor_feed_name, monitor_customer_id, monitor_customer_name, new_customer_id, new_provider_id, old_customer_id, type, new_destination_path, old_destination_path, augure_application, ub_login, ub_search_id) '
		SET @sql = @sql + 'VALUES (''' + @normalizedCustomerFolderName + ''',''REST'', ''https://api.ubermetrics-technologies.com'',''' + @ub_login + ''',''' + @ub_password + ''',''' + @destination_path + ''', 2, 1, 1, ''' + @factory_application_url + ''',@ProviderID);'
		SET @sql = @sql + 'SET @newCustomerID=(SELECT MAX(new_customer_id) FROM ub_new_customers);'

		-- Table CUSTOMER_FILE_DETAILS
		SET @sql = @sql + 'INSERT INTO CUSTOMER_FILE_DETAILS ([Customer_ID],[Source_File_Type],[Source_Path],[Source_Checksum],[NextIntegrationParameter]) '
		SET @sql = @sql + 'VALUES (@newCustomerID, ''Internet'',''' + @ub_api + ''', NULL,' + @NEXT_INTEGRATION_PARAMETER + ');'
		
		-- Table SCHEDULE
		SET  @sql = @sql + 'SET @old_schedule_id = (SELECT Schedule_ID FROM Schedule WHERE Customer_ID=' + CAST(@factory_customer_id as nvarchar(20)) + ');'
		SET @sql = @sql + 'INSERT INTO SCHEDULE ([Customer_ID],[Schedule_Start_Date],[Schedule_Status]) '
		SET @sql = @sql + 'OUTPUT INSERTED.Schedule_ID, INSERTED.Customer_ID, ' + CAST(@factory_customer_id as nvarchar(20)) + ', @old_schedule_id INTO dbo.[ub_new_schedules] (new_schedule_id, new_customer_id, old_schedule_id, old_customer_id) '
		SET @sql = @sql + 'VALUES (@newCustomerID, ''' + @SCHEDULE_START_DATE + ''',' + CAST(@SCHEDULE_STATUS as nvarchar(1)) + ');'
		  
		SET @counter_done = @counter_done + 1
		PRINT @sql
END 
	ELSE 
	BEGIN 
		SET @counter_not_done = @counter_not_done + 1
		PRINT '-- ' + @factory_customer_name + ' (ID=' + CAST(@factory_customer_id as nvarchar(10)) + ') - ' + ISNULL(@json_feed_id,'') + ' - ' + ISNULL(@factory_monitor_key,'') + ' -> Search not Found'
	END
	FETCH NEXT FROM customer_cursor INTO @factory_customer_id, @factory_customer_name, @factory_destination_path, @factory_application_url, @json_customer_id, @json_customer_name, @json_customer_name_normalized, @json_feed_id, @json_feed_name, @json_feed_name_normalized, @ub_login, @ub_password, @ub_folder_id, @factory_monitor_key
END 
CLOSE customer_cursor
DEALLOCATE customer_cursor
PRINT ''
PRINT '------------------------------------------------------------'
PRINT '-- INFO - ' + CAST(@counter_done as nvarchar(10)) + ' feeds replaced - ' + CAST(@counter_not_done as nvarchar(10)) + ' feeds not replaced'
PRINT '------------------------------------------------------------'
PRINT ''


-- CREATE NEW FEEDS FOR NEWSLETTERS
DECLARE newsletter_cursor CURSOR FOR
SELECT DISTINCT ub.json_customer_id, ub.json_customer_name, ub.[json_customer_name_normalized], ub.json_feed_id, ub.json_feed_name, ub.[json_feed_name_normalized], ub.ub_login, ub.ub_password, ub.ub_name
FROM json_newsletters nl
	INNER JOIN [dbo].[matchings.all] ub ON nl.feed_id = ub.json_feed_id
WHERE nl.feed_id NOT IN (
	SELECT DISTINCT ub.json_feed_id
	FROM [dbo].[matchings.all] ub 
		INNER JOIN factory_feeds ff ON ub.json_feed_key = ff.Monitor_Key
)
OPEN newsletter_cursor
FETCH NEXT FROM newsletter_cursor INTO @json_customer_id, @json_customer_name, @json_customer_name_normalized, @json_feed_id, @json_feed_name, @json_feed_name_normalized, @ub_login, @ub_password, @ub_folder_id

SET @counter_done = 0
SET @counter_not_done = 0
WHILE @@FETCH_STATUS = 0  
BEGIN 
	IF @ub_folder_id IS NOT NULL 
	BEGIN 
		SET @normalizedCustomerFolderName = @provider_name + '_' + REPLACE(@ub_login,'-Augure-API', '') + '_' +  @json_customer_name_normalized + @json_feed_name_normalized
		SET @ub_api = '/v2/mentions?searches.id=' + cast(@ub_folder_id as nvarchar(20)) + '&document.published.geq={0}' --&highlights=true&highlightTag=b'
		SET @destination_path= @destination_path_base + '/' + @normalizedCustomerFolderName + '/feed.xml'
		
		-- Try to find a Publisher application from login or existing Factory feeds
		SET @application_url = (SELECT [app_url] FROM [ub.accounts] WHERE [login]=@ub_login)
		IF @application_url ='???'
			SET @application_url = (SELECT DISTINCT TOP 1 aa.[url] FROM factory_feeds ff
				LEFT JOIN [dbo].[matchings.all] ub ON ff.Monitor_Key = ub.json_feed_key
				LEFT JOIN [augure.apps] aa ON aa.url LIKE '%' + ff.ApplicationName
			WHERE ub.json_customer_id=@json_customer_id)
	
		IF @application_url IS NULL AND @json_customer_id = 35768 -- '[Spain-Augure-API].[Mapfre Asistencia]%' 
			SET @application_url = 'http://mapfre.hosting.augure.com/Augure_Mapfre'
		IF @application_url IS NULL AND @json_customer_id = 36032 --'[Spain-Augure-API].[Novartis Farmacéutica S.A]%'
			SET @application_url = 'http://novartis.hosting.augure.com/Augure_Novartis'
		IF @application_url IS NULL AND @json_customer_id in (43652,43956) -- '[Spain-Augure-API].[Repsol Marketing]%'
			SET @application_url = 'https://repsol.hosting.augure.com/Augure_Repsol'
		IF @application_url IS NULL AND @json_customer_id = 39780 -- '[Spain-Augure-API].[Teatro Franco Parenti]%'
			SET @application_url = 'http://teatrofrancoparenti.hosting.augure.com/Augure_TFP'
		IF @application_url IS NULL AND @json_customer_id = 34698 -- '[France-Augure-API].[Warner]%'
			SET @application_url = 'https://warner.hosting.augure.com/Augure_Warner'
		IF @application_url IS NULL 
			SET @application_url = '???' 

		-- Table CUSTOMERS
		SET @sql = 'INSERT INTO CUSTOMERS (Customer_Name,  SourceConnectionProtocol, SourceConnectionUrl, SourceConnectionUsername , SourceConnectionPassword, Destination_Path, FeedVersion, FeedClipDays, Customer_Status, ApplicationUrl, Provider_Id) '
		SET @sql = @sql + 'OUTPUT ' + @json_feed_id + ',''' + REPLACE(@json_feed_name, '''','') + ''',' + CAST(@json_customer_id as nvarchar(20)) + ',''' + @json_customer_name_normalized + ''', INSERTED.Customer_ID, @ProviderID, NULL, ''newsletter'', ''' + @destination_path + ''',NULL,''' + @application_url + ''',''' + @ub_login + ''',''' + @ub_folder_id + ''' INTO ub_new_customers (monitor_feed_id, monitor_feed_name, monitor_customer_id, monitor_customer_name, new_customer_id, new_provider_id, old_customer_id, type, new_destination_path, old_destination_path, augure_application, ub_login, ub_search_id) '
		SET @sql = @sql + 'VALUES (''' + @normalizedCustomerFolderName + ''',''REST'', ''https://api.ubermetrics-technologies.com'',''' + @ub_login + ''',''' + @ub_password + ''',''' + @destination_path + ''',2,1,1,''' + @application_url + ''', @ProviderID);'
		SET @sql = @sql + 'SET @newCustomerID=(SELECT MAX(new_customer_id) FROM ub_new_customers);'

		-- Table CUSTOMER_FILE_DETAILS
		SET @sql = @sql + 'INSERT INTO CUSTOMER_FILE_DETAILS ([Customer_ID],[Source_File_Type],[Source_Path],[Source_Checksum],[NextIntegrationParameter]) '
		SET @sql = @sql + 'VALUES (@newCustomerID, ''Internet'',''' + @ub_api + ''', NULL,' + @NEXT_INTEGRATION_PARAMETER + ');'
		
		-- Table SCHEDULE
		SET @sql = @sql + 'INSERT INTO SCHEDULE ([Customer_ID],[Schedule_Start_Date],[Schedule_Status]) '
		SET @sql = @sql + 'OUTPUT INSERTED.Schedule_ID, INSERTED.Customer_ID, NULL, NULL INTO dbo.[ub_new_schedules] (new_schedule_id, new_customer_id, old_schedule_id, old_customer_id) '
		SET @sql = @sql + 'VALUES (@newCustomerID, ''' + @SCHEDULE_START_DATE + ''',' + CAST(@SCHEDULE_STATUS as nvarchar(1)) + ');'

		SET @counter_done = @counter_done + 1		  
		PRINT @sql
	END 
	ELSE
	BEGIN 
		SET @counter_not_done = @counter_not_done + 1
		PRINT '-- ' + @json_customer_name + ' (ID=' + CAST(@json_customer_id as nvarchar(10)) + ')-> Search not found for feed ' + CAST(@json_feed_id as nvarchar(10))
	END
		
	FETCH NEXT FROM newsletter_cursor INTO @json_customer_id, @json_customer_name, @json_customer_name_normalized, @json_feed_id, @json_feed_name, @json_feed_name_normalized, @ub_login, @ub_password, @ub_folder_id
END 
CLOSE newsletter_cursor
DEALLOCATE newsletter_cursor
PRINT ''
PRINT '------------------------------------------------------------'
PRINT '-- INFO - ' + CAST(@counter_done as nvarchar(10)) + ' new feeds created - ' + CAST(@counter_not_done as nvarchar(10)) + ' news feeds not created'
PRINT '------------------------------------------------------------'
PRINT ''

PRINT 'SELECT c.[type], c.monitor_feed_id, c.monitor_feed_name, c.monitor_customer_id, c.new_provider_id, c.new_customer_id, c.old_customer_id, c1.Customer_Name as new_customer_name , c2.Customer_Name as old_customer_name, c.new_destination_path, c.old_destination_path, c.augure_application, c.ub_login, c.ub_search_id '
PRINT 'FROM dbo.[ub_new_customers] c '
PRINT '	LEFT JOIN Customers c1 on c1.Customer_Id=c.new_customer_id '
PRINT '	LEFT JOIN Customers c2 on c2.Customer_Id=c.old_customer_id'
--PRINT 'WHERE augure_application = ''???'''
--PRINT 'ORDER BY ub_login'

PRINT 'SELECT * FROM dbo.[ub_new_Schedules];'
PRINT 'ROLLBACK TRAN'
