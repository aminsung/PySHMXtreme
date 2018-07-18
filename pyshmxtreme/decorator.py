from numpy import array, float64
MemoryManager = None


class WriteSharedMem(object):
    """
    Decorator class which can be applied to a function to write its output to a
    PySHMXtreme segment without altering the return.

    Use:
    - set pyshmxtreme.decorator.MemoryManager to your memory management file.

    - specify @WriteSharedMem and pass the 'segment' (SHMSegment) and 'block'
      (string) keyword args.

    - if no 'segment' is passed, MemoryManager.__name__.upper() is used. raises
      a NameError if the segment does not exist.

    - if no 'block' is passed, decorated_fn.__name__ is used. fails silently if
      the block does not exist.
    """
    def __init__(self, **kwargs):
        self.segment = kwargs.get('segment', None)
        self.block = kwargs.get('block', None)

        if self.segment is None:
            try:
                self.segment = getattr(MemoryManager, __name__.split('.')[-1].upper())
            except NameError:
                raise NameError('Memory segment not recognized. Check WriteSharedMem kwargs')

    def __call__(self, rqst_function, *args, **kwargs):
        if self.block is None:
            self.block = rqst_function.__name__

        def wrapper(*args, **kwargs):
            res = rqst_function(*args, **kwargs)
            data = {self.block: array(res, dtype=float64)}
            self.segment.set(data)
            return res

        return wrapper
