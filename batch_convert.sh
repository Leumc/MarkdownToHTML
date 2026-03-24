#!/bin/bash

# 检查是否提供了目录参数
if [ -z "$1" ]; then
    echo "用法: $0 <包含md文件的目录> [模板文件路径(不含.html)]"
    echo "示例: $0 template"
    exit 1
fi

# 获取目标目录
TARGET_DIR="$1"

# 设定转换脚本的绝对路径
SCRIPT_PATH="main.py"

# 如果没有指定模板，默认使用脚本同目录下的 template (不带 .html)
TEMPLATE_PATH="${2:-template}"

# 检查目录是否存在
if [ ! -d "$TARGET_DIR" ]; then
    echo "错误: 目录 '$TARGET_DIR' 不存在。"
    exit 1
fi

echo "开始转换目录 '$TARGET_DIR' 中的 Markdown 文件..."
echo "使用的模板: ${TEMPLATE_PATH}.html"
echo "----------------------------------------"

# 遍历目录下所有的 .md 文件
for md_file in "$TARGET_DIR"/*.md; do
    # 检查是否真的有 .md 文件（防止目录为空时通配符不展开直接把 "*.md" 当成字符串）
    if [ ! -f "$md_file" ]; then
        echo "目录中没有找到 .md 文件。"
        break
    fi

    # 去除文件名的 .md 后缀，将干净的路径传给 python 脚本
    FILE_WITHOUT_EXT="${md_file%.md}"

    # 检查对应的 .html 文件是否已经存在，如果存在则跳过
    if [ -f "${FILE_WITHOUT_EXT}.html" ]; then
        echo "⏭️  已存在，跳过: ${FILE_WITHOUT_EXT}.html"
        echo "----------------------------------------"
        continue
    fi

    echo "正在转换: $md_file"
    # 使用 python3 命令执行转换脚本
    python3 "$SCRIPT_PATH" "$FILE_WITHOUT_EXT" "$TEMPLATE_PATH"

    # 检查上一条 python3 命令的退出状态码
    if [ $? -eq 0 ]; then
        echo "✅ 成功 -> ${FILE_WITHOUT_EXT}.html"
    else
        echo "❌ 失败 -> $md_file"
    fi
    echo "----------------------------------------"
done

echo "🎉 全部转换任务执行完毕！"