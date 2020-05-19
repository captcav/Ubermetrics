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