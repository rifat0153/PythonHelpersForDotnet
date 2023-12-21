from typing import Dict, Any

from dapper.sp_utils import SPUtils


class DapperHandlerGenerator:
    # strongly type the params_dict
    def generate(sp_name: str, params_dict: Dict[str, str]) -> str:
        is_query = SPUtils.get_sp_type(sp_name) == 'query'

        if is_query:
            return DapperHandlerGenerator.generate_query_handler(sp_name, params_dict)
        else:
            return DapperHandlerGenerator.generate_command_handler(sp_name, params_dict)

    def generate_command_handler(sp_name: str, params_dict: Dict[str, str]) -> str:
        # store procedure
        # CREATE PROCEDURE [dbo].[usp_alert_acknowledge_alert]
        #     @acknowledged_at DATETIME OUTPUT,
        #     @user_id INT,
        #     @alert_id INT
        # AS
        #
        # Will generate the following:
        #
        # internal sealed class AcknowledgeAlertCommandHandler(ISqlConnectionFactory sqlConnectionFactory)
        #     : IRequestHandler<AcknowledgeAlertCommand, Result<Unit>>
        # {
        #     public async Task<Result<Unit>> Handle(AcknowledgeAlertCommand request, CancellationToken cancellationToken)
        #     {
        #         using var connection = sqlConnectionFactory.Create();

        #         var parameters = new DynamicParameters();
        #         parameters.Add("@user_id", request.UserId, DbType.Int32);
        #         parameters.Add("@alert_id", request.AlertId, DbType.Int32);

        #         var command = new CommandDefinition(
        #             "[dbo].[usp_alert_acknowledge_alert]",
        #             parameters,
        #             commandType: CommandType.StoredProcedure,
        #             cancellationToken: cancellationToken
        #         );

        #         await connection.ExecuteAsync(command);

        #         return Unit.Value;
        #     }
        # }

        # get the name of the SP
        handler_name = SPUtils.handler_class_name(sp_name)
        dynamic_params_section = SPUtils.create_dynamic_params_section(
            params_dict)

        handler = f"""internal sealed class {handler_name}(ISqlConnectionFactory sqlConnectionFactory)
    : IRequestHandler<{SPUtils.request_class_name(sp_name)}, Result<Unit>>
{{

    public async Task<Result<Unit>> Handle({SPUtils.request_class_name(sp_name)} request, CancellationToken cancellationToken)
    {{
        using var connection = sqlConnectionFactory.Create();

        {dynamic_params_section}

        var command = new CommandDefinition(
            "[dbo].[{sp_name}]",
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

    def generate_query_handler(sp_name: str, params_dict: Dict[str, str]) -> str:
        return "dapper_query_handler_dummy"
