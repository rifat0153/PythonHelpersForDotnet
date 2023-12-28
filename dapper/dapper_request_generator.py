from typing import Dict, Any
from dapper.sp_utils import SPUtils
from dapper.stored_procedure import StoredProcedure


class DapperRequestGenerator:
    def __init__(self, sp: StoredProcedure):
        self.sp = sp

    def generate(self) -> str:
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
        request_name = self.sp.request_class_name()

        request_params = []
        for param_key, param_value in self.sp.sp_params_dict.items():
            if param_value["direction"] != "OUT":
                request_params.append(
                    f"public {param_value['csharp_type']} {param_value['camel_case_name']} {{ get; init; }}")

        request_params_str = "\n    ".join(request_params)
        request = f"public record {request_name} : IRequest<Result<Unit>>\n{{\n    {request_params_str}\n}}"

        return request
