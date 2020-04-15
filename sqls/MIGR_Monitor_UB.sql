use UbermetricsMigration

DECLARE @next_integration_parameter as nvarchar(10) = (SELECT CAST(DATEDIFF(SECOND,'1970-01-01',GETUTCDATE ()) AS nvarchar(10)))
DECLARE @schedule_start_date as nvarchar(10) = (SELECT CAST(CONVERT(date,GETDATE()) AS nvarchar(10)))
DECLARE @destination_path_base as nvarchar(255) = 'http://data.augure.com/factory'
DECLARE @sql as nvarchar(max) = ''
DECLARE @counter_done as int = 0
DECLARE @counter_not_done as int = 0

PRINT 'USE Factory'
PRINT 'BEGIN TRAN' 

-- CREATE PROVIDERS --
DECLARE @provider_name as nvarchar(255)
DECLARE @ub_login as nvarchar(255)
DECLARE @ub_password as nvarchar(255)

DECLARE account_cursor CURSOR FOR SELECT DISTINCT [name], [login], [password] FROM dbo.[accounts.api]
OPEN account_cursor
FETCH NEXT FROM account_cursor INTO @provider_name, @ub_login, @ub_password
	
WHILE @@FETCH_STATUS = 0  
BEGIN 
	SET @sql = 'IF NOT EXISTS(SELECT 1 FROM PROVIDER WHERE ProviderFTPUser=''' + @ub_login + ''' AND ProviderFTPPassword=''' + @ub_password + ''') '
	SET @sql = @sql + 'INSERT INTO [dbo].[PROVIDER] ([Provider_Name],[ProviderFTP],[ProviderFTPUser],[ProviderFTPPassword],[Provider_Mode],[Provider_Status],[Provider_Type],[Provider_Transform_Filename],[IsFileDeleted],[DownloadLimitInDays],[IsDedicatedWatcherNeeded]) '
    SET @sql = @sql + 'VALUES ('''+ @provider_name + ''',''https://api.ubermetrics-technologies.com'',''' + @ub_login + ''',''' + @ub_password + ''',NULL,1,''REST'',''UBERMETRICS'',0,0,0);'

	SET @counter_done = @counter_done + 1
	PRINT @sql

	FETCH NEXT FROM account_cursor INTO @provider_name, @ub_login, @ub_password
END 
CLOSE account_cursor
DEALLOCATE account_cursor
PRINT ''
PRINT '------------------------------------------------------------'
PRINT '-- INFO - ' + CAST(@counter_done as nvarchar(10)) + ' new providers created'
PRINT '------------------------------------------------------------'
PRINT ''

-- CREATE CUSTOMERS --
DECLARE @factory_customer_id as nvarchar(255)
DECLARE @factory_customer_name as nvarchar(255)
DECLARE @factory_destination_path as nvarchar(255)	
DECLARE @factory_application_url as nvarchar(255)
DECLARE @json_customer_id as nvarchar(255)
DECLARE @json_customer_name as nvarchar(255)	
DECLARE @json_feed_id as nvarchar(255)
DECLARE @json_feed_name as nvarchar(255)
DECLARE @ub_folder_id as nvarchar(255)

DECLARE customer_cursor CURSOR FOR
SELECT DISTINCT  ff.Customer_ID, ff.Customer_Name, ff.Destination_Path, ff.applicationUrl, ub.json_customer_id, ub.json_customer_name, ub.json_feed_id, ub.json_feed_name, ub.ub_login, ub.ub_password, ub.ub_name
FROM factory_feeds ff  
	LEFT JOIN [dbo].[matchings.all] ub ON ff.Monitor_Key = ub.json_feed_key
ORDER BY ub_login, json_customer_id, json_feed_id
OPEN customer_cursor
FETCH NEXT FROM customer_cursor INTO @factory_customer_id, @factory_customer_name, @factory_destination_path, @factory_application_url, @json_customer_id, @json_customer_name, @json_feed_id, @json_feed_name, @ub_login, @ub_password, @ub_folder_id

PRINT 'DECLARE @ProviderID as int;'
PRINT 'DECLARE @newCustomerID as int;'
PRINT 'IF NOT EXISTS (select * from dbo.sysobjects where id = object_id(N''[dbo].[ub_new_customers]'')) '
PRINT 'CREATE TABLE dbo.[ub_new_customers] ([customer_id] int NOT NULL, [feed_id] int NOT NULL, [provider_id] int NOT NULL) '
PRINT 'TRUNCATE TABLE dbo.[ub_new_customers];'
PRINT 'IF NOT EXISTS (select * from dbo.sysobjects where id = object_id(N''[dbo].[ub_new_schedules]'')) '
PRINT 'CREATE TABLE dbo.[ub_new_schedules] ([schedule_id] int NOT NULL, [customer_id] int NULL) '
PRINT 'TRUNCATE TABLE dbo.[ub_new_schedules];'

SET @counter_done = 0
SET @counter_not_done = 0
WHILE @@FETCH_STATUS = 0  
BEGIN 
	IF @ub_folder_id IS NOT NULL 
	BEGIN 
		DECLARE @normalizedCustomerName as nvarchar(500) = REPLACE(REPLACE('[' + @ub_login + '].[' +  @json_customer_name + '].[' + @json_feed_name + ']', '\','\\'),'''','''''')
		DECLARE @ub_api as nvarchar(500) = '/v2/mentions?searches.id=' + cast(@ub_folder_id as nvarchar(20)) + '&updated.geq={0}' --&highlights=true&highlightTag=b'

		-- Table CUSTOMERS
		SET @sql = 'SET @ProviderID=(SELECT Provider_ID FROM PROVIDER WHERE ProviderFTPUser=''' + @ub_login + ''' AND ProviderFTPPassword=''' + @ub_password + ''');'
		SET @sql = @sql + 'INSERT INTO CUSTOMERS (Customer_Name, Destination_Path, Customer_Status, Provider_Id) '
		SET @sql = @sql + 'OUTPUT INSERTED.Customer_ID,' + @json_feed_id + ', @ProviderID INTO ub_new_customers (customer_id, feed_id, provider_id) '
		SET @sql = @sql + 'VALUES (''' + @normalizedCustomerName + ''',''' + @factory_destination_path + ''', 1, @ProviderID);'
		SET @sql = @sql + 'SET @newCustomerID=(SELECT MAX(customer_id) FROM ub_new_customers);'

		-- Table CUSTOMER_FILE_DETAILS
		SET @sql = @sql + 'INSERT INTO CUSTOMER_FILE_DETAILS ([Customer_ID],[Source_File_Type],[Source_Path],[Source_Checksum],[NextIntegrationParameter]) '
		SET @sql = @sql + 'VALUES (@newCustomerID, ''Internet'',''' + @ub_api + ''', NULL,' + @next_integration_parameter + ');'
		
		-- Table SCHEDULE
		SET @sql = @sql + 'INSERT INTO SCHEDULE ([Customer_ID],[Schedule_Start_Date],[Schedule_Status]) '
		SET @sql = @sql + 'OUTPUT INSERTED.Schedule_ID, INSERTED.Customer_ID INTO dbo.[ub_new_schedules] (schedule_id, customer_id) '
		SET @sql = @sql + 'VALUES (@newCustomerID, ''' + @schedule_start_date + ''',0);'
		  
		SET @counter_done = @counter_done + 1
		PRINT @sql
END 
	ELSE 
	BEGIN 
		SET @counter_not_done = @counter_not_done + 1
		PRINT '-- ' + @factory_customer_name + ' (ID=' + CAST(@factory_customer_id as nvarchar(10)) + ')-> Search not Found'
	END
	FETCH NEXT FROM customer_cursor INTO @factory_customer_id, @factory_customer_name, @factory_destination_path, @factory_application_url, @json_customer_id, @json_customer_name, @json_feed_id, @json_feed_name, @ub_login, @ub_password, @ub_folder_id
END 
CLOSE customer_cursor
DEALLOCATE customer_cursor
PRINT ''
PRINT '------------------------------------------------------------'
PRINT '-- INFO - ' + CAST(@counter_done as nvarchar(10)) + ' feeds replaced - ' + CAST(@counter_not_done as nvarchar(10)) + ' feeds not replaced'
PRINT '------------------------------------------------------------'
PRINT ''


-- CREATE NEW FEEDS FOR NEWSLETTERS
DECLARE @destination_path AS nvarchar(500)
DECLARE newsletter_cursor CURSOR FOR
SELECT DISTINCT ub.json_customer_id, ub.json_customer_name, ub.json_feed_id, ub.json_feed_name, ub.ub_login, ub.ub_password, ub.ub_name
FROM json_newsletters nl
	INNER JOIN [dbo].[matchings.all] ub ON nl.feed_id = ub.json_feed_id
WHERE nl.feed_id NOT IN (
	SELECT DISTINCT nl.feed_id
	FROM json_newsletters nl
		INNER JOIN [dbo].[matchings.all] ub ON nl.feed_id = ub.json_feed_id
		INNER JOIN factory_feeds ff ON ub.json_feed_key = ff.Monitor_Key
)
OPEN newsletter_cursor
FETCH NEXT FROM newsletter_cursor INTO @json_customer_id, @json_customer_name, @json_feed_id, @json_feed_name, @ub_login, @ub_password, @ub_folder_id

SET @counter_done = 0
SET @counter_not_done = 0
WHILE @@FETCH_STATUS = 0  
BEGIN 
	IF @ub_folder_id IS NOT NULL 
	BEGIN 
		SET @normalizedCustomerName = REPLACE(REPLACE('[' + @ub_login + '].[' +  @json_customer_name + '].[' + @json_feed_name + ']', '\','\\'),'''','''''')
		SET @ub_api = '/v2/mentions?searches.id=' + cast(@ub_folder_id as nvarchar(20)) + '&updated.geq={0}' --&highlights=true&highlightTag=b'
		SET @destination_path= @destination_path_base + '/' + @normalizedCustomerName + '/feed.xml'

		-- Table CUSTOMERS
		SET @sql = 'SET @ProviderID=(SELECT Provider_ID FROM PROVIDER WHERE ProviderFTPUser=''' + @ub_login + ''' AND ProviderFTPPassword=''' + @ub_password + ''');'
		SET @sql = @sql + 'INSERT INTO CUSTOMERS (Customer_Name, Destination_Path, Customer_Status, Provider_Id) '
		SET @sql = @sql + 'OUTPUT INSERTED.Customer_ID,' + @json_feed_id + ', @ProviderID INTO ub_new_customers (customer_id, feed_id, provider_id) '
		SET @sql = @sql + 'VALUES (''' + @normalizedCustomerName + ''',''' + @destination_path + ''', 1, @ProviderID);'
		SET @sql = @sql + 'SET @newCustomerID=(SELECT MAX(customer_id) FROM ub_new_customers);'

		-- Table CUSTOMER_FILE_DETAILS
		SET @sql = @sql + 'INSERT INTO CUSTOMER_FILE_DETAILS ([Customer_ID],[Source_File_Type],[Source_Path],[Source_Checksum],[NextIntegrationParameter]) '
		SET @sql = @sql + 'VALUES (@newCustomerID, ''Internet'',''' + @ub_api + ''', NULL,' + @next_integration_parameter + ');'
		
		-- Table SCHEDULE
		SET @sql = @sql + 'INSERT INTO SCHEDULE ([Customer_ID],[Schedule_Start_Date],[Schedule_Status]) '
		SET @sql = @sql + 'OUTPUT INSERTED.Schedule_ID, INSERTED.Customer_ID INTO dbo.[ub_new_schedules] (schedule_id, customer_id) '
		SET @sql = @sql + 'VALUES (@newCustomerID, ''' + @schedule_start_date + ''',0);'

		SET @counter_done = @counter_done + 1		  
		PRINT @sql
	END 
	ELSE
		SET @counter_not_done = @counter_not_done + 1
		PRINT '-- ' + @json_customer_name + ' (ID=' + CAST(@json_customer_id as nvarchar(10)) + ')-> Search not found for feed ' + CAST(@json_feed_id as nvarchar(10))
	FETCH NEXT FROM newsletter_cursor INTO @json_customer_id, @json_customer_name, @json_feed_id, @json_feed_name, @ub_login, @ub_password, @ub_folder_id
END 
CLOSE newsletter_cursor
DEALLOCATE newsletter_cursor
PRINT ''
PRINT '------------------------------------------------------------'
PRINT '-- INFO - ' + CAST(@counter_done as nvarchar(10)) + ' new feeds created - ' + CAST(@counter_not_done as nvarchar(10)) + ' news feeds not created'
PRINT '------------------------------------------------------------'
PRINT ''

PRINT 'SELECT * FROM dbo.[ub_new_customers];'
PRINT 'SELECT * FROM dbo.[ub_new_Schedules];'
PRINT 'ROLLBACK TRAN'
