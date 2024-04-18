verbose = False


def vprint(*values):
    if verbose:
        print(*values)


def set_verbose(value: bool):
    global verbose
    verbose = value
