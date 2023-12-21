from dapper.dapper_generator import DapperGenerator


sp_text = """
CREATE PROCEDURE [dbo].[usp_get_alert_acknowledge_alert]
    @acknowledged_at DATETIME OUTPUT,
    @user_id INT,
    @alert_id INT
AS
"""

dapper_generator = DapperGenerator(sp_text) 

request_class = dapper_generator.generate_request_class()
print(request_class)