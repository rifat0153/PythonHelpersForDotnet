from typing import Dict, Any
from dapper.dapper_return_type_generator import DapperReturnTypeGenerator

from dapper.sp_utils import SPUtils
from dapper.stored_procedure import StoredProcedure


class DapperHandlerGenerator:
    def __init__(self, sp: StoredProcedure):
        self.sp = sp
        self.return_type_generator = DapperReturnTypeGenerator(sp)

        # IQueryHandler or ICommandHandler
        self.handler_name_type_name = sp.get_sp_type(
        ) == 'query' and 'IQueryHandler' or 'ICommandHandler'

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

        is_query = self.sp.get_sp_type() == 'query'
        handler_name = self.sp.handler_class_name()
        dynamic_params_section = self.sp.retrive_dynamic_params_section()
        request_return_type_name, request_return_type_class = self.return_type_generator.generate_return_type()

        handler = f"""internal sealed class {handler_name}(ISqlConnectionFactory sqlConnectionFactory)
    : {self.handler_name_type_name}<{self.sp.request_class_name()}, Result<{request_return_type_name}>>
{{

    public async Task<Result<{request_return_type_name}>> Handle({self.sp.request_class_name()} request, CancellationToken cancellationToken)
    {{
        using var connection = sqlConnectionFactory.Create();

        {dynamic_params_section}
     
        """

        # if the return type is a Unit, then use dapper ExecuteAsync and return Unit.Value
        if request_return_type_name == "Unit":
            handler = handler + f"""
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

        # if the return type is not a Unit and it's a command, meaning it has out parameters,
        # then use dapper ExecuteAsync and grab the out parameters
        if not is_query:
            handler = handler + f"""
            var command = new CommandDefinition(
            "[dbo].[{self.sp.sp_name}]",
            parameters,
            commandType: CommandType.StoredProcedure,
            cancellationToken: cancellationToken
        );

        await connection.ExecuteAsync(command);
        """

            # retrive the out parameters from dynamic_params
            out_params = []
            for param_key, param_value in self.sp.sp_params_dict.items():
                if param_value["direction"] == "OUT" or param_value["direction"] == "INOUT":
                    out_params.append(
                        f"var {param_value['camel_case_name']} = parameters.Get<{param_value['csharp_type']}>(\"@{param_value['name']}\");")

            out_params_str = "\n".join(out_params)

            handler = handler + f"""
        {out_params_str}

            """

            # Populate the return type class
            # return new AlertAdded(AlertId: alertId, AlertNotificationCount: alertNotificationCount);

            handler = handler + f"""
            return new {request_return_type_name}({", ".join([f"{param_value['pascal_case_name']}: {param_value['camel_case_name']}" for param_key, param_value in self.sp.sp_params_dict.items() if param_value['direction'] == 'OUT' or param_value['direction'] == 'INOUT'])});
    }}
}}
            """

            return handler

        return handler

    def generate_query_handler(self) -> str:
        """
            Generates the Dapper Query Handler from the SP params dictionary.
        """

        is_query = self.sp.get_sp_type() == 'query'
        handler_name = self.sp.handler_class_name()
        dynamic_params_section = self.sp.retrive_dynamic_params_section()
        request_return_type_name, request_return_type_class = self.return_type_generator.generate_return_type()

        handler = f"""internal sealed class {handler_name}(ISqlConnectionFactory sqlConnectionFactory)
    : {self.handler_name_type_name}<{self.sp.request_class_name()}, Result<{request_return_type_name}>>
{{

    public async Task<Result<{request_return_type_name}>> Handle({self.sp.request_class_name()} request, CancellationToken cancellationToken)
    {{
        using var connection = sqlConnectionFactory.Create();

        {dynamic_params_section}
     
        """

        # if the return type is a List<T>, then use dapper QueryAsync and return the list
        if "List" in request_return_type_name:
            handler = handler + f"""
            var command = new CommandDefinition(
            "[dbo].[{self.sp.sp_name}]",
            parameters,
            commandType: CommandType.StoredProcedure,
            cancellationToken: cancellationToken
        );

        var result = await connection.QueryAsync<{request_return_type_name}>(command);

        return result?.ToList() ?? new List<{request_return_type_name}>();
    }}
}}
            """

            return handler

        # if the return type is not a List<T> and it's a query, meaning it has a single return type,
        # then use dapper QueryFirstOrDefaultAsync and return the single object
        handler = handler + f"""
        var command = new CommandDefinition(
        "[dbo].[{self.sp.sp_name}]",
        parameters,
        commandType: CommandType.StoredProcedure,
        cancellationToken: cancellationToken
    );

        var result = await connection.QueryFirstOrDefaultAsync<{request_return_type_name}>(command);

        return result;

    }}
}}
        """

        return handler
