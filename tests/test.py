import cachemir

@cachemir.init_cache
class Foo(object):
    """
    Test class
    """
    @cachemir.cache('foo_pdf')
    def _create_foo_pdf(self, out, *args, **kws):
        """
        Creates the actual cached version of the foo in the given
        location, with the given parameters.
        """
        out.write("This is my output.")


f = Foo()
print f.get_foo_pdf(1,2,3).read()
