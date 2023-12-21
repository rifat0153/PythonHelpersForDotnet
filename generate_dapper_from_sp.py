from sp_utils import SPUtils
from dapper_handler_generator import DapperHandlerGenerator
from dapper_request_generator import DapperRequestGenerator
from typing import Dict

sp_file_name = "usp_alert_acknowledge_alert.sql"
sp_text = """
CREATE PROCEDURE [dbo].[usp_alert_acknowledge_alert]
    @acknowledged_at DATETIME OUTPUT,
    @user_id INT,
    @alert_id INT
AS
"""

sp_params : Dict[str, str] = SPUtils.retrive_sp_params(sp_text)
print(sp_params)

dapper_request = DapperRequestGenerator.generate(sp_file_name, sp_params)
print(dapper_request)

# dapper_handler = DapperHandlerGenerator.generate(sp_params) 
# print(dapper_handler)
