import logging
import inspect

def trace(fn):
    def f(*args, **kwargs):
        logging.debug(f"Calling {fn.__name__}()")
        ret = fn(*args, **kwargs)
        return ret
    async def f_async(*args, **kwargs):
        logging.debug(f"Calling {fn.__name__}()")
        ret = await fn(*args, **kwargs)
        return ret
    if inspect.iscoroutinefunction(fn):
        return f_async
    return f
