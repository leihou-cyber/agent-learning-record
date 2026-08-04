#!/usr/bin/env python3
"""复现门禁：新增的测试必须失败，而且必须是"因为对的原因"而失败。

这是整个 workflow 里最关键的一道门禁。它强制要求：在动实现代码之前，
必须先用一个会失败的测试证明自己真的理解了这个 bug。

退出码：
    0  门禁通过（测试存在、是新增的、且因断言失败而 FAIL）
    1  门禁拦截（原因见 stderr）
    2  用法或环境错误

检查项：
    1. 指定的测试节点存在且可被 pytest 收集。
    2. 运行它会产生 FAILURE（不是通过，也不是收集错误）。
    3. 失败原因是 AssertionError，而不是 ImportError/TypeError/SyntaxError。
       因为拼写错误而崩溃，不算复现了 bug。
    4. 相对基线 commit，只允许新增/修改测试文件。
       复现阶段动实现代码是不允许的。
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

TEST_PATH_RE = re.compile(r"(^|/)(tests?/|test_[^/]+\.py$|[^/]+_test\.py$)")

# 如果失败原因是下面这些，说明测试本身写坏了，而不是复现了 bug。
DISQUALIFYING = (
    "ImportError",
    "ModuleNotFoundError",
    "SyntaxError",
    "NameError",
    "AttributeError",
    "TypeError",
    "IndentationError",
    "fixture",
)


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)


def fail(msg):
    """打印拦截原因到 stderr。仅用于输出，不要依赖它的返回值做流程判断。"""
    print("BLOCKED: {}".format(msg), file=sys.stderr)


def is_test_path(path):
    return bool(TEST_PATH_RE.search(path))


def check_write_scope(repo, baseline):
    """复现阶段不允许触碰任何实现文件。"""
    res = run(["git", "diff", "--name-only", baseline], repo)
    if res.returncode != 0:
        return None, "对基线 '{}' 执行 git diff 失败：{}".format(baseline, res.stderr.strip())
    untracked = run(["git", "ls-files", "--others", "--exclude-standard"], repo)
    changed = [p for p in res.stdout.splitlines() + untracked.stdout.splitlines() if p.strip()]
    offenders = sorted({p for p in changed if not is_test_path(p)})
    return offenders, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, help="仓库根目录（pytest.ini 所在位置）")
    ap.add_argument("--test", required=True, help="复现测试的 pytest node id")
    ap.add_argument("--baseline", default="HEAD", help="用于对比写入范围的基线 commit")
    ap.add_argument("--pytest", default="pytest", help="pytest 可执行文件路径")
    ap.add_argument("--json", help="将机器可读的判定结果写入此文件")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    if not repo.is_dir():
        print("仓库不存在：{}".format(repo), file=sys.stderr)
        return 2

    verdict = {"gate": "repro", "test": args.test, "passed": False, "reason": None}

    def finish(code, reason):
        verdict["passed"] = code == 0
        verdict["reason"] = reason
        if args.json:
            Path(args.json).parent.mkdir(parents=True, exist_ok=True)
            Path(args.json).write_text(json.dumps(verdict, indent=2, ensure_ascii=False))
        return code

    # --- 检查 4：优先做，成本最低，且能拦住最严重的违规 ---
    offenders, err = check_write_scope(repo, args.baseline)
    if err:
        fail(err)
        return finish(2, err)
    if offenders:
        reason = "复现阶段只允许新增测试文件；以下实现文件被修改了：{}".format(", ".join(offenders))
        fail(reason)
        return finish(1, reason)

    # --- 检查 1：可被收集 ---
    collected = run([args.pytest, "--collect-only", "-q", args.test], repo)
    if collected.returncode != 0:
        reason = "测试节点无法被收集：{}".format(args.test)
        fail("{}\n{}".format(reason, collected.stdout[-2000:]))
        return finish(1, reason)

    # --- 检查 2 + 3：必须失败，且失败原因是断言 ---
    res = run([args.pytest, "-x", "-q", args.test], repo)
    out = res.stdout + res.stderr

    if res.returncode == 0:
        reason = "测试在未修复的代码上通过了，说明没有复现这个 bug"
        fail(
            "{}。\n可能 bug 不在你以为的位置，或者断言写得太弱。".format(reason)
        )
        return finish(1, reason)

    if "AssertionError" not in out and "assert" not in out:
        reason = "测试失败了，但不是因为断言失败；这是个写坏的测试，不是复现"
        fail("{}。\n{}".format(reason, out[-2000:]))
        return finish(1, reason)

    for bad in DISQUALIFYING:
        if bad in out and "AssertionError" not in out:
            reason = "测试因 {} 失败，而不是因为行为断言失败".format(bad)
            fail("{}。\n{}".format(reason, out[-2000:]))
            return finish(1, reason)

    print("通过：复现测试按预期因断言失败。")
    print(out.strip()[-1500:])
    return finish(0, "已复现")


if __name__ == "__main__":
    sys.exit(main())
