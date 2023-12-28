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
CREATE PROCEDURE [dbo].[usp_alert_acknowledge_alert]
    @user_id INT,
    @alert_id INT
AS
"""


# dapper_generator = DapperGenerator(sp_query)
dapper_generator = DapperGenerator(sp_command)

request_class = dapper_generator.generate_request_class()
print(request_class)

handler_class = dapper_generator.generate_handler_class()
print(handler_class)


has_return_type = DapperReturnTypeGenerator.has_return_type(sp_command)
print(has_return_type)
