from typing import Dict, Any
from sp_utils import SPUtils

class DapperRequestGenerator:
    def __init__(self, dapper_handler):
        self.dapper_handler = dapper_handler

    def generate(sp_name : str, params_dict: Dict[str, str]) -> str:
        """
            Generates the Dapper Request from the SP params dictionary.
            Example:
            For the following SP:
            CREATE PROCEDURE [dbo].[usp_alert_acknowledge_alert]
                @acknowledged_at DATETIME OUTPUT,
                @user_id INT,
                @alert_id INT
            AS
            The following request will be generated:
            public record UspAlertAcknowledgeAlertCommand : IRequest<Result<Unit>>
            {
                public DateTime AcknowledgedAt { get; init; }
                public int UserId { get; init; }
                public int AlertId { get; init; }
            }
        """
        request_name_striped = sp_name.replace("usp_", "").replace(".sql", "")
        request_name = f"{SPUtils.snake_case_to_camel_case(request_name_striped)}Command"
        request_params = []
        for param_name, param in params_dict.items():
            if param["direction"] != "OUT":
                request_params.append(f"public {param['csharp_type']} {param['camel_case_name']} {{ get; init; }}")
        request_params_str = "\n    ".join(request_params)
        request = f"public record {request_name} : IRequest<Result<Unit>>\n{{\n    {request_params_str}\n}}"
        return request
