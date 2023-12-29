from dapper.dapper_generator import DapperGenerator
from dapper.dapper_return_type_generator import DapperReturnTypeGenerator


sp_query = """
CREATE PROCEDURE [dbo].[usp_get_alert_acknowledge_alert]
    @acknowledged_at DATETIME OUTPUT,
    @user_id INT,
    @alert_id INT
AS
"""

sp_command = """
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[usp_alert_acknowledge_alert]') AND type in (N'P', N'PC'))
DROP PROC [dbo].[usp_alert_acknowledge_alert]
GO
-- =============================================
-- Author:		Ramy El Sersy
-- Create date: 24/03/2017
-- Description:	Acknowledge an alert
-- =============================================
CREATE PROCEDURE [dbo].[usp_alert_acknowledge_alert]
	@user_id INT OUT,
	@alert_id INT
AS
BEGIN
	SET NOCOUNT ON

	UPDATE tblAlert
	SET alert_state_id = 254,
		time_acknowledged = SYSUTCDATETIME(),
		acknowledged_by = @user_id
	WHERE alert_id = @alert_id
		AND alert_state_id < 254
END
GO
"""


# dapper_generator = DapperGenerator(sp_query)
dapper_generator = DapperGenerator(sp_command)

request_class = dapper_generator.generate_request_class()
print(request_class)

handler_class = dapper_generator.generate_handler_class()
print(handler_class)
