
import os
import time
import inspect
import compress_pickle
from dict_hash import sha256
from logger import logger


class Cacher:

    def __init__(self, path="/tmp/anomaly_detection_caches/", validity_time=7*24*60*60):
        self.path = path
        if not self.path.endswith("/"):
            self.path += "/"
        logger.debug(f"Caches path [{self.path}]")
        self._check_path_existance()
        self.validity_time = validity_time

    def _check_path_existance(self):
        if not os.path.isdir(self.path):
            logger.debug(f"Creating the folder [{self.path}]")
            os.mkdir(self.path)

    def there_is_cache(self, f, args, kwargs):
        filepath = self._get_filepath(f, args, kwargs)
        result = os.path.isfile(filepath)
        logger.debug(f"Does the file [{filepath}] exists? {result}")
        return result

    def is_not_expired(self, cache):
        return (time.time() - cache["time"]) <= self.validity_time

    def load_cache(self, f, args, kwargs):
        filepath = self._get_filepath(f, args, kwargs)
        result = compress_pickle.load(filepath)
        return result

    def cache(self, f, args, kwargs, result):
        filepath = self._get_filepath(f, args, kwargs)
        logger.debug(f"Saving the cache to {filepath}")
        
        obj = {
            "time":time.time(),
            "result":result
        }
        compress_pickle.dump(obj, filepath)

    def _get_hash(self,f, args, kwargs):
        # If class method skip the self argument
        # (inspect.ismethod doesn't seems to works so I assume that
        # it's a method since this is supposed to cache the training)
        args = args[1:]
        
        obj = {
                "f":f.__name__,
                "args":args,
                "kwargs":kwargs
            }
        h = sha256(str(obj))
        logger.debug(f"The hash of [{obj}] is [{h}]")
        return h

    def _get_filepath(self, f, args, kwargs):
        return self.path + self._get_hash(f, args, kwargs) + ".gz"

    def __call__(self, f):
        logger.debug(f"Adding cacher to the function {f.__name__}")
        def wrapped(*args, **kwargs):
            if self.there_is_cache(f, args, kwargs):
                logger.debug(f"Found Cache")
                cache = self.load_cache(f, args, kwargs)
                if self.is_not_expired(cache):
                    logger.debug(f"Cache not expired so it will be used.")
                    return cache["result"]
                else:
                    logger.debug(f"Cache expired")
            else:
                logger.debug("No Cache found")
            logger.debug(f"Re-newing the cache")
            result = f(*args, **kwargs)
            self.cache(f, args, kwargs, result)
            return result
        return wrapped

# Add a default istance
cacher = Cacher()