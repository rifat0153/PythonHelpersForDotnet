from typing import Dict, Any
from dapper.sp_utils import SPUtils


class DapperRequestGenerator:
    def generate(sp_name: str, params_dict: Dict[str, str]) -> str:
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
        request_name = SPUtils.request_class_name(sp_name)

        request_params = []
        for param_key, param_value in params_dict.items():
            if param_value["direction"] != "OUT":
                request_params.append(
                    f"public {param_value['csharp_type']} {param_value['camel_case_name']} {{ get; init; }}")

        request_params_str = "\n    ".join(request_params)
        request = f"public record {request_name} : IRequest<Result<Unit>>\n{{\n    {request_params_str}\n}}"

        return request
