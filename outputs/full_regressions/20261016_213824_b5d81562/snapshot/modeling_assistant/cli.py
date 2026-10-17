"""Command-line modeling, solve, verify, and append-only scenario artifacts."""

import argparse
import json
import platform
import sys
import uuid
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import scipy

from . import __version__
from .model import validate_model
from .parser import add_constraint, parse_template
from .provider import generate
from .solver import solve
from .graphs import solve_graph, report_graph, save_edges
from .dynamics import solve_dynamics, report_dynamics, save_trajectory
from .fitting import load_data, data_context, solve_fit, report_fit, save_predictions

ROOT = Path(__file__).resolve().parents[1]


def expression(terms):
    return " + ".join(f"{t['coefficient']:g}*{t['variable']}" for t in terms)


def model_markdown(model):
    direction = "最大化" if model["objective"]["sense"] == "max" else "最小化"
    lines = ["### 数学模型", "", f"{direction} {expression(model['objective']['terms'])}（{model['objective']['unit']}）", ""]
    for variable in model["variables"]:
        domain = "整数" if variable["kind"] == "integer" else "连续实数"
        upper = "无限制" if variable["upper"] is None else f"{variable['upper']:g}"
        lines.append(f"- {variable['name']}：{variable['description']}；{domain}；下界 {variable['lower']:g}；上界 {upper}；单位 {variable['unit']}")
    lines.extend(["", "约束：", ""])
    lines.extend(f"- {c['name']}：{expression(c['terms'])} {c['sense']} {c['rhs']:g}（{c['unit']}）" for c in model["constraints"])
    lines.extend(["", "假设：", ""])
    lines.extend("- " + a for a in model["assumptions"])
    return lines


def report_markdown(record):
    if record["envelope"]["model"] and record["envelope"]["model"].get("task_type") == "graph":
        return report_graph(record)
    if record["envelope"]["model"] and record["envelope"]["model"].get("task_type") == "dynamics":
        return report_dynamics(record)
    if record["envelope"]["model"] and record["envelope"]["model"].get("task_type") == "polynomial_fit":
        return report_fit(record)
    lines = ["# 数学建模与求解报告", "", f"运行时间：{record['created_at']}。输入来源：{record['backend']}。", "",
             "验证仅针对已生成模型；请对照原题核对遗漏条件、单位和假设。离线模板结果不属于大模型实验。", ""]
    if record.get("generation", {}).get("local_validation"):
        lines += ["本轮追问由本地参数校验触发，原始模型响应保存在运行记录；没有执行无效模型，也未自动修改参数。", ""]
    if record["envelope"]["status"] != "ready":
        lines += ["## 需要补充或调整", ""] + ["- " + q for q in record["envelope"]["questions"]]
        return "\n".join(lines) + "\n"
    if not record["stages"]:
        lines += model_markdown(record["envelope"]["model"])
        lines += ["", "当前仅生成模型，尚未求解。可编辑 model.json，再用 --model-file 提交求解。"]
    for index, stage in enumerate(record["stages"]):
        lines += ["", f"## 阶段 {index + 1} {stage['label']}", ""]
        lines += model_markdown(stage["model"])
        result = stage["result"]
        lines += ["", f"求解状态：{result['status']}。", "", result["message"], ""]
        if result.get("infeasibility_explanation"):
            lines += ["### 为什么不可行", "", result["infeasibility_explanation"]["summary"], ""]
        if result["values"] is not None:
            lines.extend(f"- {name} = {value:g}" for name, value in result["values"].items())
            lines += [f"- 目标值：{result['objective']:g} {stage['model']['objective']['unit']}",
                      f"- 可行性与目标复算：{'通过' if result['verification']['passed'] else '失败'}", "",
                      "| 检查 | 左值 | 关系 | 右值 | 通过 |", "|---|---:|---|---:|---|"]
            for check in result["verification"]["checks"]:
                lines.append(f"| {check['name']} | {check.get('lhs', '')} | {check.get('sense', '')} | {check.get('rhs', '')} | {'是' if check['passed'] else '否'} |")
        if index and result["status"] == "optimal" and record["stages"][0]["result"]["status"] == "optimal":
            delta = result["objective"] - record["stages"][0]["result"]["objective"]
            lines += ["", f"相对初始方案，目标值变化 {delta:+g} {stage['model']['objective']['unit']}。"]
    return "\n".join(lines) + "\n"


def save_record(record, parent):
    stamp = datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y%m%d_%H%M%S")
    directory = Path(parent) / (stamp + "_" + uuid.uuid4().hex[:8])
    directory.mkdir(parents=True, exist_ok=False)
    def write_json(name, value):
        (directory / name).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    write_json("run.json", record)
    if record["envelope"]["model"] is not None:
        write_json("model.json", record["envelope"]["model"])
    for key in ("source_model", "unit_conversion", "format_repair", "source_quote_repair"):
        if record.get("generation", {}).get(key) is not None:
            write_json(key + ".json", record["generation"][key])
    for index, stage in enumerate(record["stages"]):
        write_json(f"stage_{index + 1}_model.json", stage["model"])
    from .presentation import presentation_record, system_description
    shown, display_audit = presentation_record(record)
    write_json("presentation_audit.json", display_audit)
    report = report_markdown(shown) + "\n## 系统说明（固定模板）\n\n" + system_description(record) + "\n"
    repair = record.get("generation", {}).get("format_repair", {})
    if repair.get("action") == "applied":
        report += "\n## 本地格式修复\n\n原始响应含重复的顶层model_type，本地仅删除该字段，数学参数未改动。原始响应见run.json，修复操作、前后哈希及修复后结构见format_repair.json。此结果经过格式修复，不属于原始格式直接通过。\n"
    if record.get("generation", {}).get("source_quote_repair"):
        report += "\n## 本地原文引用修复\n\n程序仅在独立提取的原参数及单位全部一致时，将错误引用替换为真实原文片段；数学数值未改动。原引用与依据见source_quote_repair.json。此结果不属于原始直接通过。\n"
    (directory / "report.md").write_text(report, encoding="utf-8")
    if record.get("dataset") and record["envelope"]["model"] and record["envelope"]["model"].get("task_type") == "polynomial_fit":
        save_predictions(record, directory)
    if record["envelope"]["model"] and record["envelope"]["model"].get("task_type") == "dynamics":
        save_trajectory(record, directory)
    if record["envelope"]["model"] and record["envelope"]["model"].get("task_type") == "graph":
        save_edges(record, directory)
    return directory


def main(argv=None):
    parser = argparse.ArgumentParser(description="优化、拟合、动态系统与图网络的建模、求解和验证")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--demo", action="store_true", help="离线模板演示，自动追加 A <= 20")
    source.add_argument("--problem", type=Path, help="UTF-8 题目文件")
    source.add_argument("--text", help="直接输入问题文本；自由表述指定 --backend openai 或 deepseek")
    source.add_argument("--interactive", action="store_true", help="在终端输入多行问题，空行结束")
    source.add_argument("--model-file", type=Path, help="人工确认或编辑后的模型 JSON")
    parser.add_argument("--backend", choices=["template", "openai", "deepseek"], default="template")
    parser.add_argument("--llm-model", help="在线模型名称；覆盖所选服务商的环境变量及本地配置")
    parser.add_argument("--add-constraint", action="append", default=[], help="例如 'A + B <= 40'；多次指定时逐步累加")
    parser.add_argument("--prepare-only", action="store_true", help="只生成模型，供检查和编辑，不求解")
    parser.add_argument("--max-clarifications", type=int, choices=range(4), default=2, help="交互模式最多补充几轮（0–3，默认2）；每轮回答会再调用一次模型")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs" / "modeling_assistant")
    parser.add_argument("--data", type=Path, help="拟合 CSV，表头 x,y,split；split 为 train/test")
    args = parser.parse_args(argv)
    try:
        dataset = load_data(args.data) if args.data else None
        if args.data and (args.demo or args.add_constraint):
            raise ValueError("--data 不与优化演示或追加约束同用")
        if args.prepare_only and (args.demo or args.add_constraint):
            raise ValueError("--prepare-only 不与 --demo 或 --add-constraint 同用；请先检查模型再追加约束")
        if args.demo and args.backend != "template":
            raise ValueError("--demo 固定为离线模板；在线调用请显式指定 --problem")
        if args.model_file and args.backend != "template":
            raise ValueError("--model-file 直接读取模型，不调用在线后端")
        if args.model_file:
            text = args.model_file.read_text(encoding="utf-8")
            envelope = {"status": "ready", "questions": [], "model": validate_model(json.loads(text))}
            metadata = {"backend": "model_file"}
            if envelope["model"].get("task_type") == "dynamics_input":
                from .units import normalize_dynamics
                source_model = envelope["model"]
                envelope["model"], conversion = normalize_dynamics(source_model)
                metadata.update(source_model=source_model, unit_conversion=conversion)
        else:
            if args.text is not None:
                text = args.text
            elif args.interactive:
                print("输入生产计划、运输分配、拟合、动态系统或图网络问题（可多行，空行结束）：")
                lines = []
                while True:
                    try:
                        line = input()
                    except EOFError:
                        break
                    if not line.strip():
                        break
                    lines.append(line)
                text = "\n".join(lines)
            else:
                path = ROOT / "examples" / "production" / "problem.txt" if args.demo else args.problem
                text = path.read_text(encoding="utf-8")
            if not text.strip():
                raise ValueError("题目不能为空")
            if len(text) > 20000:
                raise ValueError("当前题目限制为 20000 字符")
            if dataset:
                text += data_context(dataset)
            if args.backend in ("openai", "deepseek"):
                envelope, metadata = generate(text, args.llm_model, backend=args.backend)
            else:
                envelope, metadata = parse_template(text), {"backend": "template", "llm_used": False}
        record = {"created_at": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(), "version": __version__,
                  "python": platform.python_version(), "scipy": scipy.__version__, "backend": metadata["backend"],
                  "input": text, "original_input": text, "generation": metadata, "envelope": envelope, "stages": [], "clarification_history": []}
        record["dataset"] = dataset
        saved_directory = None
        if args.interactive and args.backend in ("openai", "deepseek"):
            for round_number in range(args.max_clarifications):
                if envelope["status"] != "needs_clarification":
                    break
                # Persist every paid response before asking for another one.
                saved_directory = save_record(record, args.output)
                print("需要补充：" + "；".join(envelope["questions"]))
                print("本轮记录：" + str(saved_directory.resolve()))
                print("直接输入补充条件（一行；回车留空或 /quit 结束。提交后会再次调用模型）：")
                try:
                    answer = input().strip()
                except EOFError:
                    answer = ""
                if not answer or answer == "/quit":
                    break
                combined = text + "\n待澄清问题：" + "；".join(envelope["questions"]) + "\n用户补充条件：" + answer
                if len(combined) > 20000:
                    raise ValueError("补充后的题目超过 20000 字符；此前记录已保存")
                next_envelope, next_metadata = generate(combined, args.llm_model, backend=args.backend)
                record["clarification_history"].append({"round": round_number + 1, "questions": envelope["questions"],
                    "answer": answer, "previous_record": str(saved_directory.resolve() / "run.json")})
                text, envelope, metadata = combined, next_envelope, next_metadata
                record.update(input=text, generation=metadata, envelope=envelope)
                saved_directory = None
        is_fit = envelope["model"] is not None and envelope["model"].get("task_type") == "polynomial_fit"
        if is_fit and dataset is None:
            raise ValueError("拟合需要 --data CSV（x,y,split）；不能从模型生成数据")
        if dataset and envelope["status"] == "ready" and not is_fit:
            raise ValueError("提供了拟合数据，但模型返回优化任务，请检查题意")
        is_dynamic = envelope["model"] is not None and envelope["model"].get("task_type") == "dynamics"
        is_graph = envelope["model"] is not None and envelope["model"].get("task_type") == "graph"
        if (is_fit or is_dynamic or is_graph) and args.add_constraint:
            raise ValueError("--add-constraint 仅适用于线性优化模型")
        status = 0
        if envelope["status"] != "ready":
            status = 3
            print(envelope["status"] + ": " + "；".join(envelope["questions"]))
        elif is_graph and not args.prepare_only:
            result = solve_graph(envelope["model"])
            record["stages"].append({"label": "图网络", "model": envelope["model"], "result": result})
            print(f"图网络：{result['status']}，结果={result['value']} {envelope['model']['unit']}")
            if result.get("path"):
                print("路径：" + " → ".join(result["path"]))
            if result.get("cut"):
                print("最小割容量：" + str(result["cut"]["capacity"]))
            if not result["verification"]["passed"]:
                status = 4
        elif is_dynamic and not args.prepare_only:
            result = solve_dynamics(envelope["model"])
            record["stages"].append({"label": "动态仿真", "model": envelope["model"], "result": result})
            print(f"动态求解：{result['status']}，末时刻值={result['final_value']:.8g}，解析对照最大误差={result['max_absolute_error']:.3g}")
            if not result["verification"]["passed"]:
                status = 4
        elif is_fit and not args.prepare_only:
            result = solve_fit(envelope["model"], dataset)
            record["stages"].append({"label": "拟合", "model": envelope["model"], "result": result})
            print(f"拟合完成：阶数={result['degree']}，训练 RMSE={result['metrics']['train']['rmse']:.6g}，留出 RMSE={result['metrics']['test']['rmse']:.6g}")
            for warning in result["warnings"]:
                print("提示：" + warning)
        elif not args.prepare_only:
            model = envelope["model"]
            scenarios = [("初始模型", model)]
            additions = (["A <= 20"] if args.demo else []) + args.add_constraint
            for addition in additions:
                model = add_constraint(model, addition)
                scenarios.append(("新增 " + addition, model))
            for label, model in scenarios:
                result = solve(model)
                record["stages"].append({"label": label, "model": model, "result": result})
                print(f"{label}: {result['status']}, 决策变量={result['values']}, 目标值={result['objective']}")
                if result.get("infeasibility_explanation"):
                    print("不可行原因：" + result["infeasibility_explanation"]["summary"])
                if result["status"] not in ("optimal", "infeasible", "unbounded"):
                    status = 4
        directory = saved_directory or save_record(record, args.output)
        print("运行记录与报告：" + str(directory.resolve()))
        return status
    except (ValueError, OSError) as exc:
        print("错误：" + str(exc), file=sys.stderr)
        return 2
