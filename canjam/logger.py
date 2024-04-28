verbose = False


def vprint(*values):
    """
    Acts like the normal print function, but only prints if verbose has been
    set to true using the set_verbose function.
    """
    if verbose:
        print(*values)


def set_verbose(value: bool):
    """
    Sets the global verbose variable to the specified value.
    """
    global verbose
    verbose = value is True
