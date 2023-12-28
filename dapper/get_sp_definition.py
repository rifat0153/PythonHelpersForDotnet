import re


import re

def extract_stored_procedure_definition(sql_script):
    # Define the pattern to match the stored procedure definition
    pattern = re.compile(
        r'(CREATE PROCEDURE\s*[\s\S]*?\s*AS)', re.IGNORECASE)

    # Search for the pattern in the SQL script
    match = pattern.search(sql_script)

    if match:
        procedure_definition = match.group(1)
        return procedure_definition.strip()

    return None


# Example usage:
sql_script = """
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[usp_add_alert_trigger_mappings]') AND type in (N'P', N'PC'))
DROP PROC [dbo].[usp_add_alert_trigger_mappings]
GO
-- =============================================
-- Author:		Justin Wilkinson
-- Create date: 14/11/2019
-- Description:	Add a single alert trigger mapping to multiple locations
-- =============================================
CREATE PROCEDURE [dbo].[usp_add_alert_trigger_mappings]
	@alert_trigger_id INT,
	@tblLocationIds tpIntTable READONLY
AS
BEGIN	

	INSERT INTO tblAlertTriggerMapping
	(trigger_id, location_id)
	SELECT @alert_trigger_id, id
	FROM @tblLocationIds
	WHERE NOT EXISTS (SELECT * FROM tblAlertTriggerMapping WHERE trigger_id = @alert_trigger_id AND location_id = id);

	EXEC usp_system_update_parameter @name = 'refreshalerts', @value = '1';

END
GO
"""

sp_text = extract_stored_procedure_definition(sql_script)

print(sp_text)
