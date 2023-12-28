class DapperReturnTypeGenerator:
    def has_return_type(sp_text: str) -> bool:
        """
            Returns True if the SP has a return type.
        """
        # A SP has a return type if:
        # it has a RETURN statement.
        # or if it has OUT parameters.
        # or if it has a SELECT statement. The select has to be the first statement After Begin.

        # check if SP has select statement after BEGIN
        text_after_begin = sp_text[sp_text.find(
            "BEGIN") + len("BEGIN"):].strip().rstrip().lstrip()
        if text_after_begin.startswith("SELECT"):
            return True

        # check if SP has RETURN statement
        if "RETURN" in sp_text:
            return True

        # check if SP has OUT parameters
        if "OUTPUT" in sp_text:
            return True

        return False
