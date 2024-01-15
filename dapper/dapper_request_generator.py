from typing import Dict, Any
from dapper.dapper_return_type_generator import DapperReturnTypeGenerator
from dapper.stored_procedure import StoredProcedure


class DapperRequestGenerator:
    def __init__(self, sp: StoredProcedure):
        self.sp = sp
        self.return_type_generator = DapperReturnTypeGenerator(sp)

    def generate(self) -> [str, str]:
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

        request_return_type_name, request_return_type_class = self.return_type_generator.generate_return_type()

        request_name = self.sp.request_class_name()
        sp_params_dict = self.sp.sp_params_dict
        request_params = []

        for param_key, param_value in sp_params_dict.items():
            if param_value["direction"] != "OUT":
                request_params.append(
                    f"public {param_value['csharp_type']} {param_value['pascal_case_name']} {{ get; init; }}")

        request_params_str = "\n    ".join(request_params)
        request = f"\npublic record {request_name} : IRequest<Result<{request_return_type_name}>>\n{{\n    {request_params_str}\n}}\n"

        # if SP has a return type, then add it to the request
        # if request_return_type_class:
        #     request = request + "\n\n" + request_return_type_class + "\n\n"

        return request, request_return_type_class
