import unittest
import cachemir

class CachemirTestCase(unittest.TestCase):
    def setUp(self):
        # Create the example class.
        @cachemir.init_cache
        class Foo(object):
            """
            Test class
            """
            @cachemir.cache('get_foo_pdf')
            def _create_foo_pdf(self, out, *args, **kws):
                """
                Creates the actual cached version of the foo in the given
                location, with the given parameters.
                """
                out.write("This is my output.")
        self.Foo = Foo

    def test_get_output(self):
        f = self.Foo()
        self.assertEqual(f.get_foo_pdf(1,2,3).read(), "This is my output.")

if __name__ == '__main__':
    unittest.main()
