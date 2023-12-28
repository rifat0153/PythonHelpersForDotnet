from typing import Dict, Any

from dapper.sp_utils import SPUtils
from dapper.stored_procedure import StoredProcedure


class DapperHandlerGenerator:
    def __init__(self, sp: StoredProcedure):
        self.sp = sp

    # strongly type the params_dict

    def generate(self) -> str:

        is_query = self.sp.get_sp_type() == 'query'

        if is_query:
            return self.generate_query_handler()
        else:
            return self.generate_command_handler()

    def generate_command_handler(self) -> str:
        """
            Generates the Dapper Command Handler from the SP params dictionary.
        """

        handler_name = self.sp.handler_class_name()
        dynamic_params_section = self.sp.retrive_dynamic_params_section()

        handler = f"""internal sealed class {handler_name}(ISqlConnectionFactory sqlConnectionFactory)
    : IRequestHandler<{self.sp.request_class_name()}, Result<Unit>>
{{

    public async Task<Result<Unit>> Handle({self.sp.request_class_name()} request, CancellationToken cancellationToken)
    {{
        using var connection = sqlConnectionFactory.Create();

        {dynamic_params_section}

        var command = new CommandDefinition(
            "[dbo].[{self.sp.sp_name}]",
            parameters,
            commandType: CommandType.StoredProcedure,
            cancellationToken: cancellationToken
        );

        await connection.ExecuteAsync(command);

        return Unit.Value;
    }}
}}
        """

        return handler

    def generate_query_handler(sp: StoredProcedure) -> str:
        return "dapper_query_handler_dummy"
