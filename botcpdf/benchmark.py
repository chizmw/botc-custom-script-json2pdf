import os
import time

def timeit(f):

    def timed(*args, **kw):

        ts = time.time()
        result = f(*args, **kw)
        te = time.time()

        # we know we're only using this for class methogs, so we can
        # assume the first arg is self
        # only print the timings if BOTC_TIMER is set
        if os.environ.get("BOTC_TIMER"):
            print(f"func:{f.__name__} args: [{args[1:]}] took: {te-ts} sec")
        return result

    return timed
