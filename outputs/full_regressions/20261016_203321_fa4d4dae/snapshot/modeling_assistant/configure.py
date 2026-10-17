"""Run locally in a terminal; key entry is hidden and never logged."""

import argparse
import getpass
import sys

from .config import PROVIDERS, config_path, credentials, save_config


def main(argv=None):
    parser = argparse.ArgumentParser(description="配置官方模型 API；不会发送网络请求")
    parser.add_argument("--provider", choices=list(PROVIDERS), default="openai")
    parser.add_argument("--check", action="store_true", help="只检查本地配置是否完整，不验证服务权限")
    args = parser.parse_args(argv)
    provider = PROVIDERS[args.provider]
    try:
        if not args.check:
            if not sys.stdin.isatty():
                raise ValueError("请在本机交互式终端运行配置向导，不要把密钥传入命令行参数")
            print("服务地址：" + provider["endpoint"])
            print(f"密钥以本地文件保存（非加密，仅本人可读写）：{config_path(args.provider)}")
            key = getpass.getpass(f"粘贴 {args.provider} API Key（输入不可见）：")
            model = input(f"模型 ID [{provider['default_model']}]：").strip() or provider["default_model"]
            save_config(key, model, args.provider)
        key, model = credentials(backend=args.provider)
        print("服务商：" + args.provider)
        print("API 密钥：" + ("已配置" if key else "未配置"))
        print("模型：" + (model or "未配置"))
        print("优先级：命令行模型 > 环境变量 > 本地配置。")
        print("此检查未联网，不代表密钥有效、模型有权限或账户有额度。")
        return 0 if key and model else 2
    except (ValueError, OSError, EOFError, KeyboardInterrupt) as exc:
        print("配置未完成：" + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
