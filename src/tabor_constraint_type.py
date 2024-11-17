class TaborConstraintType(object):
    valid_constraints = ("on", "length")

    def __init__(self, constraint: str) -> None:
        if constraint not in self.valid_constraints:
            raise Exception(f"{constraint} is not a valid constraint, valid constraints are  {str(self.valid_constraints)}")

        self.type = constraint
