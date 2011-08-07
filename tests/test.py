import subprocess
import unittest
import cachemir

class CachemirTestCase(unittest.TestCase):
    def setUp(self):
        # Create the example class.
        @cachemir.cache_init
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

            @cachemir.cache('get_qr')
            def _create_qr(self, out):
                """
                Creates a qr code for  url based. Requires qrencode.
                """
                cmd = [
                    "qrencode",
                    "-o", "-",
                    "-m", "0",
                    "http://github.com/idmillington/cachemir"
                    ]
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                out.write(proc.stdout.read())
                out.close()

        self.Foo = Foo

    def test_get_output(self):
        f = self.Foo()
        self.assertEqual(f.get_foo_pdf(1,2,3).read(), "This is my output.")

    def test_external(self):
        """
        Tests the generation with an external routine (qrencode in this case).
        """
        f = self.Foo()
        qr = f.get_qr().read()
        self.assert_(len(qr) > 100)
        self.assertEqual(qr[:4], '\x89PNG')

if __name__ == '__main__':
    unittest.main()
