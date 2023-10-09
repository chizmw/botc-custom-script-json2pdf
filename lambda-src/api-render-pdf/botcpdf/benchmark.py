""" A simple decorator to time functions. """
import os
import time


def timeit(fcall):
    """A simple decorator to time functions."""

    def timed(*args_used, **kw):
        """The actual decorator function."""
        tstart = time.time()
        result = fcall(*args_used, **kw)
        tend = time.time()

        # we know we're only using this for class methogs, so we can
        # assume the first arg is self
        # only print the timings if BOTC_TIMER is set
        if os.environ.get("BOTC_TIMER"):
            args_used = args_used[1:]
            # stringify args and truncate at 50 chars
            # args_used = [str(arg)[:50] for arg in args_used]

            # stringify args and truncate at 50 chars, if we truncated add a ...
            args_used = [
                str(arg)[:50] + ("..." if len(str(arg)) > 50 else "")
                for arg in args_used
            ]

            # if we don't have any args, use 'none' instead of an empty list
            if not args_used:
                args_used = "none"

            print(f"func:{fcall.__name__} args: [{args_used}] took: {tend-tstart} sec")
        return result

    return timed
