"""跨平台卫生检查：脚本里不能有非 ASCII 标识符。

为什么要查：Python 3 允许非 ASCII 标识符，但中文标识符在某些终端/编码环境里
会出问题，而且中文只该出现在注释和字符串里。

单独成文件（而不是塞进 CI 的 heredoc）：Windows runner 默认 shell 是 PowerShell，
不认 bash 的 `<<'PY'` 语法 ⇒ 写成 .py 才能三平台统一跑。
"""
import ast
import sys

FILES = [
    "skills/formula-typesetting/scripts/formula_norm.py",
    "skills/formula-typesetting/scripts/pptx_omml_inject.py",
]


def main():
    ok = True
    for f in FILES:
        try:
            src = open(f, encoding="utf-8").read()
        except OSError as e:
            print("SKIP  %s (%s)" % (f, e))
            continue
        try:
            tree = ast.parse(src)
        except SyntaxError as e:
            print("FAIL  %s 语法错误: %s" % (f, e))
            ok = False
            continue
        bad = [n.name for n in ast.walk(tree)
               if isinstance(n, (ast.FunctionDef, ast.ClassDef))
               and any(ord(c) > 127 for c in n.name)]
        if bad:
            print("FAIL  %s 含非 ASCII 标识符: %s" % (f, bad))
            ok = False
        else:
            print("OK    %s" % f)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
