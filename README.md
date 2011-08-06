# Cachemir

A package for cached derived data on Python objects.

A common use-case that comes up for me in Web applications is where
objects (or ORM models) have derived files calculated from the base
data. It might be that I use an object to generate a PDF document or
an image, for example. I want the generated document to be cached.

## Simple Example

Decorate the class and functions that generate derived data.

    import cachemir

    @cachemir.cache_init
    class Foo(ORMModel):
        @cachemir.cache('get_pdf')
        def _generate_pdf(self, out_file):
            # ... do pdf generating magic ...
            out_file.close()

Now we can use this by:

    f = Foo()
    return HttpResponse(
        f.get_pdf().read(),
        mimetype="application/pdf"
        )

The important bit is just the `f.get_pdf()` which returns a file-like
object from which the derived data can be read.

## Documentation

To use the system, apply the `@cachemir.cache_init` decorator to the
**class** (without this the system will have no effect), and the
`@cachemir.cache` decorator to functions that can generate derived
content.

The `cachemir.cache` decorator takes a required argument, which is the
new method you want Cachemir to generate for you, which will return
the derived data, creating it if required.

## Storage

There are a number of places where you might want to put the cached
data. The most common are on the hard-drive and in memory. But it
would also be advisable to leverage the power of other tools such as
**Redis** and **memcached**.

To support this Cachemir uses a pluggable storage system. In the
`storage` sub-module the `CacheStorage` class defines the
interface. There are two useful subclasses provided:
`CacheLocalStorage` is an in-memory store and `CacheFileStorage` is a
disk-backed store. To specify a storage, pass an *instance* of the
storage through the `storage_obj` keyword argument to the `cache`
decorator:

    import cachemir

    @cachemir.cache_init
    class Foo(ORMModel):
        @cachemir.cache(
	    'get_pdf',
	    storage_obj=cachemir.storage.CacheLocalStorage()
	    )
        def _generate_pdf(self, out_file):
            # ... do pdf generating magic ...
            out_file.close()

The `CacheFileStorage` takes an optional directory to write the
content in. By default it uses a git-style mechanism of using
subdirectories named for the first-two characters of the filenames it
is writing. If you want to do something different, you can subclass
`CacheFileStorage` and override its `get_path` method.

If you create a new storage backend (by subclassing `CacheStorage` and
overriding its `has`, `get`, and `out` methods), fork and issue a
pull-request.


## Key generation

The system stores the cached data against a unique key. This allows
the same content to map to the same file (in some of my use cases,
lots of folks create essentially empty objects, which we don't want
multiple copies of). So the system has to calculate the key from the
data. It does this in two phases. Firstly it tries to work out a
unique representation for the object itself, and secondly it converts
any additional arguments passed in to a unique representation.

The latter means that if you call `get_pdf('a4')` you'll get a
different cached result that `get_pdf('letter')`.

By default the unique representation of the object is calculated with
a Python hash. This will normally need to be overridden:

    @cachemir.cache('get_pdf', uid_fn=lambda x:str(x.pk))
    def _generate_pdf(self, out_file):
    	....

The arguments are then combined with this object-specific
representation and hashed with `SHA1` to get the final key. If you
want a different way to calculate this, or you want to ignore some
parameters for the purposes of generating a hash, you can give a
`hash_fn` argument:

    def generate_hash(obj, *args, **kws):
    	return hashlib.sha256(...).hexdigest()

    @cachemir.cache('get_pdf', hash_fn=generate_hash)
    def _generate_pdf(self, out_file):
        ....

Most often, however, you don't need to worry about this, and you can
use the default. It is mostly important when you want to be able to
independently query the cache (such as when you want to serve files
from a disk-backed storage through a static webserver, for example).