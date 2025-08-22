#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 .env 文件中的环境变量是否被 config/config.py 正确加载
"""
import os
import sys
from dotenv import dotenv_values
import importlib.util

# 获取项目根目录（即 tests 的上一级目录）
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 1. 读取 .env 文件
ENV_PATH = os.path.join(PROJECT_ROOT, '.env')
if not os.path.exists(ENV_PATH):
    ENV_PATH = os.path.join(PROJECT_ROOT, '.env.example')
    if not os.path.exists(ENV_PATH):
        print('未找到 .env 或 .env.example 文件，无法检查！')
        sys.exit(1)

env_vars = dotenv_values(ENV_PATH)

# 2. 导入 config/config.py
config_path = os.path.join(PROJECT_ROOT, 'config', 'config.py')
spec = importlib.util.spec_from_file_location('config', config_path)
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)

# 3. 检查变量一致性
print(f"\n对比 {os.path.relpath(ENV_PATH, PROJECT_ROOT)} 与 config/config.py 加载结果：\n")
all_ok = True
for key, env_val in env_vars.items():
    # 跳过注释和空行
    if not key or key.strip().startswith('#'):
        continue
    # config.py 变量名一般全大写
    config_val = getattr(config, key, None)
    if config_val is None:
        print(f"[未加载] {key} 在 config.py 中未找到！")
        all_ok = False
    else:
        # 统一类型为字符串对比
        config_val_str = str(config_val)
        env_val_str = str(env_val)
        if config_val_str == env_val_str:
            print(f"[一致]   {key} = {env_val_str}")
        else:
            print(f"[不一致] {key}: .env='{env_val_str}'  |  config.py='{config_val_str}'")
            all_ok = False

if all_ok:
    print("\n✅ 所有 .env 变量都被 config.py 正确加载！")
else:
    print("\n❌ 存在未加载或不一致的变量，请检查上方输出！") 