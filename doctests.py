if __name__ == "__main__":
    import doctest
    import hbforty

    doctest.testmod(
        hbforty,
        optionflags=doctest.NORMALIZE_WHITESPACE
    )
