ALTER FUNCTION [dbo].[fn_normalized]
(
	@customerName nvarchar(200)
)
RETURNS nvarchar(500)
AS
BEGIN
	DECLARE @result as nvarchar(500) =	TRIM(LOWER(@customerName))

	SET @result = REPLACE(@result, ' ','')
	SET @result = REPLACE(@result, '''', '')
	SET @result = REPLACE(@result, ',', '-')
	SET @result = REPLACE(@result, '_', '')
	SET @result = REPLACE(@result, '.', '')
	SET @result = REPLACE(@result, '(', '-')
	SET @result = REPLACE(@result, ')', '')
	SET @result = REPLACE(@result, '+', '-')

	-- Diacritics characters
	SET @result = REPLACE(@result, 'ó', 'o')
	SET @result = REPLACE(@result, 'õ', 'o')
	SET @result = REPLACE(@result, 'ö', 'o')
	SET @result = REPLACE(@result, 'í', 'i')
	SET @result = REPLACE(@result, 'á', 'a')
	SET @result = REPLACE(@result, 'à', 'a')
	SET @result = REPLACE(@result, 'ã', 'a')
	SET @result = REPLACE(@result, 'é', 'e')
	SET @result = REPLACE(@result, 'è', 'e')
	SET @result = REPLACE(@result, 'ê', 'e')
	SET @result = REPLACE(@result, 'ñ', 'n')

	-- Reserved characters 
	SET @result = REPLACE(@result, ';', '') 
	SET @result = REPLACE(@result, '/', '') 
	SET @result = REPLACE(@result, '?', '') 
	SET @result = REPLACE(@result, ':', '') 
	SET @result = REPLACE(@result, '@', '') 
	SET @result = REPLACE(@result, '=', '') 
	SET @result = REPLACE(@result, '&', '')

	-- Unsafe characters
	SET @result = REPLACE(@result, '"', '')
	SET @result = REPLACE(@result, '<', '')
	SET @result = REPLACE(@result, '>', '')
	SET @result = REPLACE(@result, '#', '')
	SET @result = REPLACE(@result, '%', '')
	SET @result = REPLACE(@result, '{', '')
	SET @result = REPLACE(@result, '}', '')
	SET @result = REPLACE(@result, '|', '')
	SET @result = REPLACE(@result, '\', '')
	SET @result = REPLACE(@result, '^', '')
	SET @result = REPLACE(@result, '~', '')
	SET @result = REPLACE(@result, '[', '')
	SET @result = REPLACE(@result, ']', '')
	SET @result = REPLACE(@result, '`', '')

	RETURN @result
END
