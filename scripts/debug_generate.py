import importlib.util, pathlib
spec = importlib.util.spec_from_file_location('pysharp_main', str(pathlib.Path(__file__).resolve().parents[1] / 'pysharp.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

src_try = '''
try {
    print("hi");
} catch (Exception e) {
    print(e);
} finally {
    print("done");
}
'''
print('---TRY GENERATED---')
print(mod.convert(src_try))

src_using = '''
using (var f = open("/dev/null")) {
    print("ok");
}
'''
print('---USING GENERATED---')
print(mod.convert(src_using))

src_method = '''
public void greet(int x, string y) {
    print(x);
    print(y);
}
'''
print('---METHOD GENERATED---')
print(mod.convert(src_method))
