from dapper.sp_utils import SPUtils
from dapper.stored_procedure import StoredProcedure


class DapperReturnTypeGenerator:
    def __init__(self, sp: StoredProcedure):
        self.sp = sp

    # return a tuple with name of the return type and the return type class definition if it has one.
    def generate_return_type(self) -> tuple[str, str | None]:
        """
            Returns the return type of the SP. If the SP has no return type, meaning its a command, then returns Result<Unit>.
            A SP has a return type if:
                it has a RETURN statement.
                or if it has OUT parameters.
                or if it has a SELECT statement. The select has to be the first statement After Begin.
            This method will return a tuple with name of the return type and the return type class definition if it has one.
            Unit will return Unit with no class definition.
        """
        sp = self.sp

        sp_has_return_type = sp.has_return_type()

        # if SP has no return type, then return Unit
        if not sp_has_return_type:
            return "Unit", None

        sp_definition = sp.sp_definition
        sp_params_dict = sp.sp_params_dict
        sp_name = sp.sp_name

        # get the return type name
        return_type_name = self.get_return_type_name()

        # if the SP is a command and has a return type, meaning it has a RETURN statement, then return Result<Unit>
        # create a class definition for the return type with the OUT parameters
        if sp.get_sp_type() == "command":
            return_type_class_definition = self.get_command_return_type_class_definition()
            return f"{return_type_name}", return_type_class_definition

        # if the SP is a query and has a return type, meaning it has a SELECT statement and might have OUT parameters

        return "Query Test", "Query Test"

    def get_command_return_type_class_definition(self) -> str:
        """
            Returns the class definition for the return type of a command SP.
            Example:
            For the following SP:
            CREATE PROCEDURE [dbo].[usp_alert_acknowledge_alert]
                @acknowledged_at DATETIME OUTPUT,
                @user_id INT,
                @alert_id INT
            AS
            The following class definition will be returned:
            public record UspAlertAcknowledgeAlertResult
            {
                public DateTime AcknowledgedAt { get; init; }
                public int UserId { get; init; }
                public int AlertId { get; init; }
            }
        """

        sp_params_dict = self.sp.sp_params_dict
        return_type_class_definition = []

        for param_key, param_value in sp_params_dict.items():
            if param_value["direction"] == "OUTPUT" or param_value["direction"] == "INOUT" or param_value["direction"] == "OUT":
                return_type_class_definition.append(
                    f"public {param_value['csharp_type']} {param_value['pascal_case_name']} {{ get; init; }}")

        return_type_class_definition_str = "\n    ".join(
            return_type_class_definition)
        return_type_class_definition = f"\npublic record {self.get_return_type_name()}\n{{\n    {return_type_class_definition_str}\n}}\n"
        return return_type_class_definition

    def get_return_type_name(self):
        """
            Returns the name of the return type. for sp name: usp_get_alert_acknowledge_alert, the return type name will be UspGetAlertAcknowledgeAlertResult.
        """
        sp = self.sp
        return_type_name = f"{SPUtils.snake_case_to_pascal_case(sp.sp_name)}Result"
        return return_type_name
