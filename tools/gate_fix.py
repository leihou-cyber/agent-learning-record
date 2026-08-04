#!/usr/bin/env python3
"""修复门禁：复现测试必须转为 PASS，全量测试必须全绿，
且复现测试本身不能被"削弱"过。

退出码：
    0  门禁通过
    1  门禁拦截
    2  用法或环境错误

检查项：
    1. 复现测试文件的内容必须与复现阶段提交时逐字节一致。
       这是反作弊的核心：LLM 最容易犯的错误就是把测试改到能通过为止。
    2. 复现测试现在必须通过。
    3. 全量测试套件必须全绿，且收集到的测试数量不能减少。
       数量变少说明有测试被删除或被跳过了。
    4. 改动范围必须限制在 --allow 指定的路径内（默认 src/）。
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

COUNT_RE = re.compile(r"(\d+) passed")


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)


def fail(msg):
    print("BLOCKED: {}".format(msg), file=sys.stderr)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def node_to_file(node_id):
    return node_id.split("::")[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--test", required=True, help="复现测试的 pytest node id")
    ap.add_argument("--test-sha", required=True,
                    help="复现阶段记录下来的测试文件 sha256")
    ap.add_argument("--baseline-count", type=int, required=True,
                    help="复现阶段收集到的测试总数")
    ap.add_argument("--allow", default="src/",
                    help="逗号分隔，允许修复阶段改动的路径前缀")
    ap.add_argument("--pytest", default="pytest")
    ap.add_argument("--json")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    allow = [p.strip() for p in args.allow.split(",") if p.strip()]
    verdict = {"gate": "fix", "test": args.test, "passed": False, "reason": None, "checks": {}}

    def finish(code, reason):
        verdict["passed"] = code == 0
        verdict["reason"] = reason
        if args.json:
            Path(args.json).parent.mkdir(parents=True, exist_ok=True)
            Path(args.json).write_text(json.dumps(verdict, indent=2, ensure_ascii=False))
        return code

    # --- 检查 1：复现测试未被篡改 ---
    test_file = repo / node_to_file(args.test)
    if not test_file.is_file():
        reason = "复现测试文件不见了：{}".format(test_file)
        fail(reason)
        return finish(1, reason)
    actual = sha256(test_file)
    verdict["checks"]["test_sha"] = actual
    if actual != args.test_sha:
        reason = "复现测试文件在修复阶段被改动过"
        fail(
            "{}。\n  期望 sha256 {}\n  实际 sha256 {}\n"
            "修复应该只改实现代码，绝不能改这个失败的测试。".format(
                reason, args.test_sha, actual
            )
        )
        return finish(1, reason)

    # --- 检查 4：写入范围 ---
    diff = run(["git", "diff", "--name-only", "HEAD"], repo)
    untracked = run(["git", "ls-files", "--others", "--exclude-standard"], repo)
    changed = [p for p in diff.stdout.splitlines() + untracked.stdout.splitlines() if p.strip()]
    offenders = sorted({p for p in changed if not any(p.startswith(a) for a in allow)})
    verdict["checks"]["changed"] = changed
    if offenders:
        reason = "修复改动了 {} 之外的文件：{}".format(allow, ", ".join(offenders))
        fail(reason)
        return finish(1, reason)

    # --- 检查 2：复现测试现在必须通过 ---
    res = run([args.pytest, "-q", args.test], repo)
    if res.returncode != 0:
        reason = "复现测试仍然失败，说明 bug 没修好"
        fail("{}。\n{}".format(reason, (res.stdout + res.stderr)[-2000:]))
        return finish(1, reason)

    # --- 检查 3：全量套件全绿，且数量没有减少 ---
    full = run([args.pytest, "-q"], repo)
    out = full.stdout + full.stderr
    if full.returncode != 0:
        reason = "全量测试套件没有全绿，这次修复引入了回归"
        fail("{}。\n{}".format(reason, out[-3000:]))
        return finish(1, reason)

    m = COUNT_RE.search(out)
    count = int(m.group(1)) if m else -1
    verdict["checks"]["passed_count"] = count
    verdict["checks"]["baseline_count"] = args.baseline_count
    if count < args.baseline_count:
        reason = "测试数量从 {} 降到了 {}，说明有测试被删除或跳过".format(
            args.baseline_count, count
        )
        fail(reason)
        return finish(1, reason)

    print("通过：复现测试转绿，全量套件全绿（{} passed，基线 {}）。".format(
        count, args.baseline_count))
    return finish(0, "已修复")


if __name__ == "__main__":
    sys.exit(main())
