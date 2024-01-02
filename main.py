from dapper.dapper_generator import DapperGenerator
from dapper.dapper_return_type_generator import DapperReturnTypeGenerator


sp_query = """
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[usp_get_alert_severity_image_urls]') AND type in (N'P', N'PC'))
DROP PROC [dbo].[usp_get_alert_severity_image_urls]
GO
-- =============================================
-- Author:		Ramy El Sersy
-- Create date: 16/05/2014
-- Description:	Return a alert severity image URLs
-- =============================================
CREATE  PROCEDURE [dbo].[usp_get_alert_severity_image_urls]
	@alert_trigger_id INT
AS
BEGIN
	SELECT *
	FROM tblAlertSeverityImageUrl
	ORDER BY alert_severity_colour_id;
END
GO
"""

sp_query1 = """
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[usp_alerts_get_alert_notification_mappings]') AND type in (N'P', N'PC'))
DROP Procedure  [dbo].[usp_alerts_get_alert_notification_mappings]
GO
CREATE Procedure usp_alerts_get_alert_notification_mappings
	@alert_trigger_id INT
AS 
BEGIN
	SELECT vwUserWithBranding.user_id,
		vwUserWithBranding.tenant_id, 
		vwUserWithBranding.first_name,
		vwUserWithBranding.last_name, 
		vwUserWithBranding.full_name,
		vwUserWithBranding.email, 
		vwUserWithBranding.mobile,
		vwUserWithBranding.tenant_role_id,
		vwUserWithBranding.is_global_admin,
		vwUserWithBranding.permissions_last_updated,
		vwUserWithBranding.login_url,
		vwUserWithBranding.email_sender_name,
		vwUserWithBranding.email_sender_email,
		vwUserWithBranding.alert_email_footer
	FROM vwUserWithBranding
	RIGHT JOIN (
		SELECT DISTINCT user_id
		FROM tblAlertNotificationUserMapping
		WHERE alert_trigger_id = @alert_trigger_id
	) tMappedUserIds
		ON tMappedUserIds.user_id = vwUserWithBranding.user_id
	WHERE vwUserWithBranding.user_id IS NOT NULL
	ORDER BY vwUserWithBranding.full_name;
END
GO
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
dapper_generator = DapperGenerator(sp_query1)
# dapper_generator = DapperGenerator(sp_command)

request_class = dapper_generator.generate_request_class()
print(request_class)

handler_class = dapper_generator.generate_handler_class()
print(handler_class)
