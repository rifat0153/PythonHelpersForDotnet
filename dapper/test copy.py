class DapperGenerator:
    @staticmethod
    def generate_handler(sp_name, sp_params):
        # Generate request class
        request_class_name = f"Add{sp_name.replace('[dbo].[usp_', '').replace(']', '').replace('add_', '').replace('_', '')}Command"
        request_properties = "\n".join(
            [f"    public {param['type']} {param['name']} {{ get; init; }}" for param in sp_params])
        request_class = f"public record {request_class_name} : IRequest<Result<{request_class_name}Result>>\n{{\n{request_properties}\n}}"

        # Generate handler class
        handler_class_name = f"{request_class_name}Handler"
        handler_properties = "\n".join(
            [f"            parameters.Add(\"@{param['name']}\", request.{param['name']}, DbType.{param['db_type']});" for param in sp_params])
        output_params = "\n".join(
            [f"            parameters.Add(\"@{param['name']}_out\", DbType.{param['db_type']}, direction: ParameterDirection.Output);" for param in sp_params if param.get('is_output', False)])
        result_class = f"public record {request_class_name}Result(int AlertId, int NotificationCount);"

        handler_class = f"""internal sealed class {handler_class_name} : IRequestHandler<{request_class_name}, Result<{request_class_name}Result>>
{{
    private readonly ISqlConnectionFactory _sqlConnectionFactory;

    public {handler_class_name}(ISqlConnectionFactory sqlConnectionFactory)
    {{
        _sqlConnectionFactory = sqlConnectionFactory;
    }}

    public async Task<Result<{request_class_name}Result>> Handle({request_class_name} request, CancellationToken cancellationToken)
    {{
        using var connection = _sqlConnectionFactory.Create();

        var parameters = new DynamicParameters();
{handler_properties}
{output_params}
        
        var command = new CommandDefinition(
            \"[dbo].{sp_name.replace('[dbo].[', '').replace(']', '')}\",
            parameters,
            commandType: CommandType.StoredProcedure,
            cancellationToken: cancellationToken
        );

        await connection.ExecuteAsync(command);

        var alertId = parameters.Get<int>("@alert_id_out");
        var alertNotificationCount = parameters.Get<int>("@alert_notification_count_out");

        return new {request_class_name}Result(alertId, alertNotificationCount);
    }}
}}"""

        return request_class, result_class, handler_class


# Example usage:
sp_name = "[dbo].[usp_add_alert]"
sp_params = [
    {"name": "location_id", "type": "int", "db_type": "Int32", "is_output": False},
    {"name": "time_raised", "type": "DateTime?",
        "db_type": "DateTime", "is_output": False},
    {"name": "alert_trigger_id", "type": "int?",
        "db_type": "Int32", "is_output": False},
    # Add other parameters as needed
]

request_class, result_class, handler_class = DapperGenerator.generate_handler(
    sp_name, sp_params)
print(request_class)
print(result_class)
print(handler_class)
