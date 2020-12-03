BEGIN TRAN
    -- Activation des schedules
	UPDATE Schedule
	  SET Schedule_Status = 1
	FROM Schedule s
	INNER JOIN ub_new_schedules  us ON s.Schedule_ID=us.new_schedule_id

	SELECT * 
	FROM Schedule s
		INNER JOIN ub_new_schedules us ON s.Schedule_ID=us.new_schedule_id
ROLLBACK TRAN 


-- MIGRATION 01-10-2020
	SELECT * FROM [UbermetricsMigration].[dbo].[augure.apps]
	WHERE 
	[name] in (
		'15 Love', 
		'IDEEAL CONSEIL',
		'ACF',
		'ATOS', 
		'Musée de la Chasse et de la Nature', 
		'Fenwick Linde', 
		'FONDATION EDF',
		'INRA',
		'institut montaigne',
		'La Plagne',
		'Mazda',
		'Agence Raoul',
		'sanef',
		'terre majeure',
		'Versailles Grand Parc',
		'Château de Versailles',
		'Vinci autoroutes - Autoroutes du sud de la France',
		'Vox&Co',
		'Agence Cartel',
		'Agence Olivia Payerne'
	) 

SELECT TOP (1000) [monitor_feed_id]
      ,[monitor_feed_name]
      ,[monitor_customer_id]
      ,[monitor_customer_name]
      ,[new_customer_id]
      ,[new_provider_id]
      ,[old_customer_id]
      ,[type]
      ,[new_destination_path]
      ,[old_destination_path]
      ,[augure_application]
      ,[ub_login]
      ,[ub_search_id]
FROM [UberFactory].[dbo].[ub_new_customers]
WHERE augure_application in (
	'https://acf.hosting.augure.com/Augure_ACF'
	,'https://cartel.hosting.augure.com/Augure_Cartel'
	,'https://oliviapayerne.hosting.augure.com/Augure_OP'
	,'https://raoul.hosting.augure.com/Augure_Raoul'
	,'https://atos.hosting.augure.com/Augure_Atos'
	,'https://versailles.hosting.augure.com/Augure_Versailles'
	,'https://fenwick.hosting.augure.com/Augure_Fenwick'
	,'https://edf.hosting.augure.com/Augure_FondationEDF'
	,'https://ideealconseil.hosting.augure.com/Augure_IdeealConseil'
	,'https://inra.hosting.augure.com/Augure_INRA'
	,'https://institut-montaigne.hosting.augure.com/Augure_InstitutMontaigne'
	,'https://la-plagne.hosting.augure.com/Augure_LaPlagne'
	,'https://mazda.hosting.augure.com/Augure_Mazda'
	,'https://chassenature.hosting.augure.com/Augure_CN'
	,'https://sanef.hosting.augure.com/Augure_SANEF'
	,'https://terremajeure.hosting.augure.com/Augure_TerreMajeure'
	,'https://versaillesagglo.hosting.augure.com/Augure_VGP'
	,'https://vinci.hosting.augure.com/Augure_Vinci'
	,'https://voxco.hosting.augure.com/Augure_VoxCo'
	,'https://15love.hosting.augure.com/Augure_15Love'
)
ORDER BY augure_application



-- MIGRATION 25-11-2020
	SELECT * FROM [UbermetricsMigration].[dbo].[augure.apps]
	WHERE 
	[name] in (
		'Keima',
		'Adocom',
		'Eliotrope'
	) 

-- MIGRATION 01-12-2020
SELECT * FROM [UbermetricsMigration].[dbo].[augure.apps]
WHERE [name] in (
		'Alima',
		'CRC',
		'LITTLE WING',
		'Santé Publique France',
		'Volvo'
)
