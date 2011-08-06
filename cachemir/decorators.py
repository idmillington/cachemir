import storage

def cache(name, uid_fn=lambda x:str(hash(x)), storage=None, hash_fn=None):
    """
    Marks a function as being able to calculate and saved a cached
    version of the class's data. The wrapped function should take a
    file-like objet as its first argument, and any number of
    additional configuration arguments.
    """
    def _decorator(fn):
        # Unlike most decorators, we don't proxy the underlying
        # function, we just add the cache config data.
        fn.__cache_config = (name, uid_fn, storage, hash_fn)
        return fn
    return _decorator

def init_cache(Class):
    """
    Go through each cached method and add the relevant methods.
    """
    for fn_name in dir(Class):
        fn = getattr(Class, fn_name)
        if callable(fn) and hasattr(fn, "__cache_config"):
            # Find the cache configuration
            name, uid_fn, storage, hash_fn = fn.__cache_config

            # Use default storage in a temporary directory if we don't
            # have one.
            if storage is None:
                storage = storage.CacheFileStorage()

            # Create the get function
            def __get(self, *args, **kws):
                # Calculate the data hash.
                if hash_fn is not None:
                    data_hash = hash_fn(self, *args, **kws)
                else:
                    uid = uid_fn(self)
                    # TODO: Add the args and kws values to the hash.
                    data_hash = uid

                # See if we have copy.
                if not storage.has(data_hash):
                    # Do this the explicit way (rather than the newer
                    # 'with' statement) as not every file-like may be a
                    # context.
                    out = storage.out(data_hash)
                    try:
                        # Create the data.
                        fn(self, out, *args, **kws)
                    finally:
                        out.close()

                    # Sanity check
                    assert storage.has(data_hash)

                # Created or not, return the file-like for the data.
                return storage.get(data_hash)

            # Save the get function
            get_fn_name = "get_%s" % name
            __get.__name__ = get_fn_name
            setattr(Class, get_fn_name, __get)

            # Remove the config data.
            del fn.im_func.__cache_config

    # The class is modified, but we don't need to return a proxy.
    return Class

