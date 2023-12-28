class DapperGenerator:
    @staticmethod
    def generate_handler(sp_name, sp_params):
        # Generate request class
        request_class_name = f"Create{sp_name}Command"
        request_properties = "\n".join(
            [f"    public {param['type']} {param['name']} {{ get; set; }}" for param in sp_params])
        request_class = f"public record {request_class_name} : IRequest<Result<Unit>>\n{{\n{request_properties}\n}}"

        # Generate handler class
        handler_class_name = f"{request_class_name}Handler"
        handler_properties = "\n".join(
            [f"            parameters.Add(\"@{param['name']}\", request.{param['name']}, DbType.{param['db_type']});" for param in sp_params])
        handler_class = f"""internal sealed class {handler_class_name} : IRequestHandler<{request_class_name}, Result<Unit>>
{{
    private readonly ISqlConnectionFactory _sqlConnectionFactory;

    public {handler_class_name}(ISqlConnectionFactory sqlConnectionFactory)
    {{
        _sqlConnectionFactory = sqlConnectionFactory;
    }}

    public async Task<Result<Unit>> Handle({request_class_name} request, CancellationToken cancellationToken)
    {{
        try
        {{
            using var connection = _sqlConnectionFactory.Create();

            var parameters = new DynamicParameters();
{handler_properties}
            var command = new CommandDefinition(
                \"[dbo].{sp_name}\",
                parameters,
                commandType: CommandType.StoredProcedure,
                cancellationToken: cancellationToken
            );

            var a = await connection.ExecuteAsync(command);

            return Unit.Value;
        }}
        catch (Exception ex)
        {{
            return new Result<Unit>(ex);
        }}
    }}
}}"""

        return request_class, handler_class


# Example usage:
sp_name = "usp_add_alert_trigger_mappings"
sp_params = [
    {"name": "alert_trigger_id", "type": "int", "db_type": "Int32"},
    {"name": "tblLocationIds", "type": "int[]", "db_type": "Int32"}
]

request_class, handler_class = DapperGenerator.generate_handler(
    sp_name, sp_params)
print(request_class)
print(handler_class)
