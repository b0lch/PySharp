import unittest
import importlib.util
import pathlib

# Load the top-level pysharp.py as a module so tests use the same convert() implementation.
spec = importlib.util.spec_from_file_location(
    "pysharp_main",
    str(pathlib.Path(__file__).resolve().parents[1] / "pysharp.py"),
)
pysharp_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pysharp_main)


class TestCSharpFeatures(unittest.TestCase):
    def compile_and_check(self, source: str):
        code = pysharp_main.convert(source)
        # ensure it compiles
        compile(code, '<generated>', 'exec')
        return code

    def test_for_loop(self):
        src = '''
int n = 5;
for (int i = 0; i < n; i++) {
    print(i);
}
'''
        code = self.compile_and_check(src)
        self.assertIn('for i in range(0, n):', code)

    def test_try_catch_finally(self):
        src = '''
try {
    print("hi");
} catch (Exception e) {
    print(e);
} finally {
    print("done");
}
'''
        code = self.compile_and_check(src)
        self.assertIn('try:', code)
        self.assertIn('except Exception as e:', code)
        self.assertIn('finally:', code)

    def test_using_to_with(self):
        src = '''
using (var f = open("/dev/null")) {
    print("ok");
}
'''
        code = self.compile_and_check(src)
        self.assertIn('with open("/dev/null") as f:', code)

    def test_method_declaration(self):
        src = '''
public void greet(int x, string y) {
    print(x);
    print(y);
}
'''
        code = self.compile_and_check(src)
        self.assertIn('def greet(x, y):', code)

    def test_lambda_expression(self):
        src = 'var f = x => x + 1;'
        code = self.compile_and_check(src)
        self.assertIn('lambda x: x + 1', code)

if __name__ == '__main__':
    unittest.main()
