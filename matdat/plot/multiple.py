from .action import DuplicateArg


def multiple(*arg):
    return DuplicateArg(*arg)
