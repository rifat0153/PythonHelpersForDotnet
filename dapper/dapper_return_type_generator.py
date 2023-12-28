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
            Unit will return Result<Unit> with no class definition.
        """
        sp = self.sp

        sp_has_return_type = sp.has_return_type()

        # if SP has no return type, then return Result<Unit>
        if not sp_has_return_type:
            return "Result<Unit>", None

        sp_definition = sp.sp_definition
        sp_params_dict = sp.sp_params_dict
        sp_name = sp.sp_name

        # check if SP has select statement after BEGIN
        return "Test", "Test"
