	use UbermetricsMigration

	DECLARE @NEXT_INTEGRATION_PARAMETER as nvarchar(20) = '637450560000000000' -- http://www.datetimetoticks-converter.com/
	DECLARE @SCHEDULE_START_DATE as nvarchar(10) = '2020-12-30'
	DECLARE @SCHEDULE_STATUS as bit = 1

	DECLARE @destination_path_base as nvarchar(255) = 'https://data.hosting.augure.com/uberfactory'
	DECLARE @sql as nvarchar(max) = ''
	DECLARE @counter_done as int = 0
	DECLARE @counter_not_done as int = 0

	PRINT 'USE UberFactory'
	PRINT 'BEGIN TRAN' 

	-- RETRIEVE UBERMETRICS PROVIDER ID  --
	DECLARE @provider_name as nvarchar(255) = 'Ubermetrics'
	PRINT 'DECLARE @ProviderID as int =(SELECT Provider_ID FROM PROVIDER WHERE Provider_Name=''' + @provider_name + ''');'

	-- CREATE CUSTOMERS --
	DECLARE @ub_login as nvarchar(255)
	DECLARE @ub_password as nvarchar(255)
	DECLARE @factory_customer_id as nvarchar(255)
	DECLARE @factory_customer_name as nvarchar(255)
	DECLARE @factory_destination_path as nvarchar(255)	
	DECLARE @factory_monitor_key as nvarchar(255)
	DECLARE @destination_path AS nvarchar(500)
	DECLARE @application_url as nvarchar(500)
	DECLARE @json_customer_id as nvarchar(255)
	DECLARE @json_customer_name as nvarchar(255)	
	DECLARE @json_customer_name_normalized as nvarchar(255)	
	DECLARE @json_feed_id as nvarchar(255)
	DECLARE @json_feed_name as nvarchar(255)
	DECLARE @json_feed_name_normalized as nvarchar(255)
	DECLARE @ub_folder_id as nvarchar(255)

	DECLARE customer_cursor CURSOR FOR
	SELECT DISTINCT ff.Customer_ID, 
					ff.Customer_Name, 
					ff.Destination_Path,
					CASE 
						WHEN ub.augure_application IS NOT NULL AND LEN(ub.augure_application)>0 THEN ub.augure_application
						ELSE aa.[url]
					END as 'url_selected',
					ub.monitor_customer_id, 
					ub.monitor_customer_name, 
					ub.json_customer_name_normalized, 
					ub.monitor_feed_id, 
					ub.monitor_feed_name, 
					ub.json_feed_name_normalized, 
					ub.ub_login, ub.ub_password, 
					ub.ub_name, 
					ff.Monitor_Key
	FROM factory_feeds ff
		LEFT JOIN [dbo].[matchings_normalized] ub ON ff.Monitor_Key = ub.monitor_feed_key
		LEFT JOIN [augure.apps] aa ON aa.url LIKE '%' + ff.ApplicationName
	WHERE ub.monitor_feed_id not in (SELECT DISTINCT feed_id FROM uberfactory)
	ORDER BY ub_login, monitor_customer_id, monitor_feed_id

	OPEN customer_cursor
	FETCH NEXT 
	FROM customer_cursor INTO 
	@factory_customer_id, 
	@factory_customer_name, 
	@factory_destination_path, 
	@application_url, 
	@json_customer_id, 
	@json_customer_name, 
	@json_customer_name_normalized,
	@json_feed_id, 
	@json_feed_name, 
	@json_feed_name_normalized, 
	@ub_login, 
	@ub_password, 
	@ub_folder_id, 
	@factory_monitor_key

	PRINT 'DECLARE @newCustomerID as int;'
	PRINT 'DECLARE @old_schedule_id as int;'
	PRINT 'IF NOT EXISTS (select * from dbo.sysobjects where id = object_id(N''[dbo].[ub_new_customers]'')) '
	PRINT 'CREATE TABLE dbo.[ub_new_customers] ([monitor_feed_id] int NOT NULL, [monitor_feed_name] nvarchar(500) NULL, [monitor_customer_id] int NOT NULL, [monitor_customer_name] nvarchar(100) NOT NULL, [new_customer_id] int NOT NULL, [new_provider_id] int NOT NULL, [old_customer_id] int NULL, [type] nvarchar(20) NOT NULL, [new_destination_path] nvarchar(500) NOT NULL, [old_destination_path] nvarchar(500) NULL, [augure_application] nvarchar(500) NULL, ub_login nvarchar(100) NOT NULL, ub_search_id int NOT NULL); '
	PRINT 'TRUNCATE TABLE dbo.[ub_new_customers];'
	PRINT 'IF NOT EXISTS (select * from dbo.sysobjects where id = object_id(N''[dbo].[ub_new_schedules]'')) '
	PRINT 'CREATE TABLE dbo.[ub_new_schedules] ([new_schedule_id] int NOT NULL, [new_customer_id] int NULL, [old_customer_id] int NULL) '
	PRINT 'TRUNCATE TABLE dbo.[ub_new_schedules];'

	SET @counter_done = 0
	SET @counter_not_done = 0
	WHILE @@FETCH_STATUS = 0  
	BEGIN 
		IF @ub_folder_id IS NOT NULL 
		BEGIN 
			DECLARE @normalizedCustomerFolderName as nvarchar(500) = @provider_name + '_' + REPLACE(REPLACE(@ub_login,'-Augure-API',''), 'ó','o') + '_' +  @json_customer_name_normalized + @json_feed_name_normalized
			DECLARE @ub_api as nvarchar(500) = '/v2/mentions?searches.id=' + cast(@ub_folder_id as nvarchar(20)) + '&document.published.geq={0}' --&highlights=true&highlightTag=b'
			SET @destination_path= @destination_path_base + '/' + @normalizedCustomerFolderName + '/feed.xml'

			-- Table CUSTOMERS
			SET @sql = 'INSERT INTO CUSTOMERS (Customer_Name, SourceConnectionProtocol, SourceConnectionUrl, SourceConnectionUsername , SourceConnectionPassword, Destination_Path, FeedVersion, FeedClipDays, Customer_Status, ApplicationUrl, Provider_Id) '
			SET @sql = @sql + 'OUTPUT ' + @json_feed_id + ',''' + REPLACE(@json_feed_name, '''','') + ''',' + CAST(@json_customer_id as nvarchar(20)) + ',''' + @json_customer_name_normalized + ''', INSERTED.Customer_ID, @ProviderID, ' + CAST(@factory_customer_id AS nvarchar(20)) + ', ''factory'', ''' + @destination_path + ''',''' + @factory_destination_path + ''',''' + @application_url + ''',''' + @ub_login + ''',''' + @ub_folder_id + ''' INTO ub_new_customers (monitor_feed_id, monitor_feed_name, monitor_customer_id, monitor_customer_name, new_customer_id, new_provider_id, old_customer_id, type, new_destination_path, old_destination_path, augure_application, ub_login, ub_search_id) '
			SET @sql = @sql + 'VALUES (''' + @normalizedCustomerFolderName + ''',''REST'', ''https://api.ubermetrics-technologies.com'',''' + @ub_login + ''',''' + @ub_password + ''',''' + @destination_path + ''', 2, 1, 1, ''' + @application_url + ''',@ProviderID);'
			SET @sql = @sql + 'SET @newCustomerID=(SELECT MAX(new_customer_id) FROM ub_new_customers);'

			-- Table CUSTOMER_FILE_DETAILS
			SET @sql = @sql + 'INSERT INTO CUSTOMER_FILE_DETAILS ([Customer_ID],[Source_File_Type],[Source_Path],[Source_Checksum],[NextIntegrationParameter]) '
			SET @sql = @sql + 'VALUES (@newCustomerID, ''Internet'',''' + @ub_api + ''', NULL,' + @NEXT_INTEGRATION_PARAMETER + ');'
			
			-- Table SCHEDULE
			SET @sql = @sql + 'INSERT INTO SCHEDULE ([Customer_ID],[Schedule_Start_Date],[Schedule_Status]) '
			SET @sql = @sql + 'OUTPUT INSERTED.Schedule_ID, INSERTED.Customer_ID, ' + CAST(@factory_customer_id as nvarchar(20)) + ' INTO dbo.[ub_new_schedules] (new_schedule_id, new_customer_id, old_customer_id) '
			SET @sql = @sql + 'VALUES (@newCustomerID, ''' + @SCHEDULE_START_DATE + ''',' + CAST(@SCHEDULE_STATUS as nvarchar(1)) + ');'
			
			SET @counter_done = @counter_done + 1
			PRINT @sql
	END 
		ELSE 
		BEGIN 
			SET @counter_not_done = @counter_not_done + 1
			PRINT '-- ' + @factory_customer_name + ' (ID=' + CAST(@factory_customer_id as nvarchar(10)) + ') - ' + ISNULL(@json_feed_id,'') + ' - ' + ISNULL(@factory_monitor_key,'') + ' -> Search not Found'
		END
		FETCH NEXT FROM customer_cursor INTO @factory_customer_id, @factory_customer_name, @factory_destination_path, @application_url, @json_customer_id, @json_customer_name, @json_customer_name_normalized, @json_feed_id, @json_feed_name, @json_feed_name_normalized, @ub_login, @ub_password, @ub_folder_id, @factory_monitor_key
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
	SELECT DISTINCT ub.monitor_customer_id, 
					ub.monitor_customer_name, 
					ub.json_customer_name_normalized, 
					ub.monitor_feed_id, ub.monitor_feed_name, 
					ub.json_feed_name_normalized, 
					ub.ub_login, ub.ub_password, 
					ub.ub_name, 
					ub.augure_application
	FROM json_newsletters nl
		INNER JOIN [dbo].[matchings_normalized] ub ON nl.feed_id = ub.monitor_feed_id
	WHERE ub.monitor_feed_id NOT IN (
		SELECT DISTINCT ub.monitor_feed_id
		FROM [dbo].[matchings_normalized] ub 
			INNER JOIN factory_feeds ff ON ub.monitor_feed_key = ff.Monitor_Key
	)
	AND ub.monitor_feed_id NOT IN (SELECT feed_id FROM uberfactory)
	ORDER BY ub_login, monitor_customer_id, monitor_feed_id

	OPEN newsletter_cursor
	FETCH NEXT 
	FROM newsletter_cursor INTO 
	@json_customer_id, 
	@json_customer_name, 
	@json_customer_name_normalized, 
	@json_feed_id, @json_feed_name, 
	@json_feed_name_normalized, 
	@ub_login, @ub_password, 
	@ub_folder_id,
	@application_url

	SET @counter_done = 0
	SET @counter_not_done = 0
	WHILE @@FETCH_STATUS = 0  
	BEGIN 
		IF @ub_folder_id IS NOT NULL 
		BEGIN 
			SET @normalizedCustomerFolderName = @provider_name + '_' + REPLACE(REPLACE(@ub_login,'-Augure-API', ''),'ó','o') + '_' +  @json_customer_name_normalized + @json_feed_name_normalized
			SET @ub_api = '/v2/mentions?searches.id=' + cast(@ub_folder_id as nvarchar(20)) + '&document.published.geq={0}' --&highlights=true&highlightTag=b'
			SET @destination_path= @destination_path_base + '/' + @normalizedCustomerFolderName + '/feed.xml'

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
			SET @sql = @sql + 'OUTPUT INSERTED.Schedule_ID, INSERTED.Customer_ID, NULL INTO dbo.[ub_new_schedules] (new_schedule_id, new_customer_id, old_customer_id) '
			SET @sql = @sql + 'VALUES (@newCustomerID, ''' + @SCHEDULE_START_DATE + ''',' + CAST(@SCHEDULE_STATUS as nvarchar(1)) + ');'

			SET @counter_done = @counter_done + 1		  
			PRINT @sql
		END 
		ELSE
		BEGIN 
			SET @counter_not_done = @counter_not_done + 1
			PRINT '-- ' + @json_customer_name + ' (ID=' + CAST(@json_customer_id as nvarchar(10)) + ')-> Search not found for feed ' + CAST(@json_feed_id as nvarchar(10))
		END
			
		FETCH NEXT FROM newsletter_cursor INTO @json_customer_id, @json_customer_name, @json_customer_name_normalized, @json_feed_id, @json_feed_name, @json_feed_name_normalized, @ub_login, @ub_password, @ub_folder_id, @application_url
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
