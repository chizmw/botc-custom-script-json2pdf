""" A simple decorator to time functions. """
import os
import time


def timeit(fcall):
    """A simple decorator to time functions."""

    def timed(*args, **kw):
        """The actual decorator function."""
        tstart = time.time()
        result = fcall(*args, **kw)
        tend = time.time()

        # we know we're only using this for class methogs, so we can
        # assume the first arg is self
        # only print the timings if BOTC_TIMER is set
        if os.environ.get("BOTC_TIMER"):
            print(f"func:{fcall.__name__} args: [{args[1:]}] took: {tend-tstart} sec")
        return result

    return timed
