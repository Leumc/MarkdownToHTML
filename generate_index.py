import os
import sys
import re

def print_usage():
    print("用法: python3 generate_index.py <需要生成索引的根目录> [目录模板文件路径(不含.html)]")
    print("示例: python3 generate_index.py ./NoteBook ./index_template")
    sys.exit(1)

if len(sys.argv) < 2:
    print_usage()

target_dir = sys.argv[1]
# 默认使用同级目录下的 index_template.html
template_path = sys.argv[2] + ".html" if len(sys.argv) > 2 else "index_template.html"

if not os.path.isdir(target_dir):
    print(f"错误: 目标目录 '{target_dir}' 不存在。")
    sys.exit(1)

if not os.path.isfile(template_path):
    print(f"错误: 模板文件 '{template_path}' 不存在。")
    sys.exit(1)

# 1. 读取模板
try:
    with open(template_path, "r", encoding="utf-8") as f:
        template_content = f.read()
except Exception as e:
    print(f"读取模板文件失败: {e}")
    sys.exit(1)

# 2. 递归构建目录树 HTML 的核心函数
def build_html_tree(current_dir, base_dir):
    html = ''
    try:
        items = sorted(os.listdir(current_dir))
    except PermissionError:
        return ""

    folders = []
    files = []
    
    # 分类和过滤
    for item in items:
        if item.startswith('.') or item == 'index.html' or item == '__pycache__' or item == 'image': 
            continue # 跳过隐藏文件、缓存、旧的索引文件以及 image 文件夹
        
        full_path = os.path.join(current_dir, item)
        if os.path.isdir(full_path):
            folders.append(item)
        elif os.path.isfile(full_path) and item.endswith('.html'):
            if item == os.path.basename(template_path) or item == 'template.html': continue # 跳过目录模板自身和页面模板
            files.append(item)

    # 优先渲染文件夹
    if folders:
        html += '<div class="folder-list">\n'
        for folder in folders:
            full_path = os.path.join(current_dir, folder)
            svg_folder = '<svg class="svg-icon folder-icon" viewBox="0 0 16 16"><path d="M1.75 1A1.75 1.75 0 0 0 0 2.75v10.5C0 14.216.784 15 1.75 15h12.5A1.75 1.75 0 0 0 16 13.25v-8.5A1.75 1.75 0 0 0 14.25 3H7.543l-1.6-1.684A1.75 1.75 0 0 0 4.715 1H1.75Z"/></svg>'
            html += f'<div class="folder-wrapper">\n<div class="folder-item" onclick="toggleFolder(this)">{svg_folder} <span>{folder}</span></div>\n'
            html += '<div class="folder-content">\n'
            html += build_html_tree(full_path, base_dir)
            html += '</div>\n</div>\n'
        html += '</div>\n'
        
    # 随后渲染文件
    if files:
        html += '<div class="file-grid">\n'
        for file in files:
            full_path = os.path.join(current_dir, file)
            rel_path = "NoteBook/"+os.path.relpath(full_path, base_dir) # 获取相对路径供 href 跳转使用
            display_name = file[:-5] # 去除 .html 后缀作为显示名
            
            # 读取对应的 md 文件提取知识点和模板标签
            md_file_path = full_path[:-5] + '.md'
            tags = []
            if os.path.exists(md_file_path):
                try:
                    with open(md_file_path, 'r', encoding='utf-8') as mf:
                        md_text = mf.read(2048) # 只读前 2KB 加快速度
                        meta_match = re.search(r'^---\s*\n(.*?)\n---\s*\n', md_text, re.DOTALL)
                        if meta_match:
                            raw_meta = meta_match.group(1)
                            current_key = None
                            for line in raw_meta.split('\n'):
                                line_strip = line.strip()
                                if not line_strip: continue
                                if ':' in line_strip and not line_strip.startswith('-'):
                                    current_key = line_strip.split(':', 1)[0].strip()
                                elif line_strip.startswith('-') and current_key in ['知识点', '模板']:
                                    tags.append(line_strip[1:].strip())
                except Exception:
                    pass
            
            tags_html = ""
            if tags:
                tags_html = '<div class="tag-container">' + "".join([f'<span class="index-tag">{t}</span>' for t in tags]) + '</div>'
            
            svg_file = '<svg class="svg-icon file-icon" viewBox="0 0 16 16"><path d="M2 1.75C2 .784 2.784 0 3.75 0h6.586c.464 0 .909.184 1.237.513l2.914 2.914c.329.328.513.773.513 1.237v9.586A1.75 1.75 0 0 1 13.25 16H3.75A1.75 1.75 0 0 1 2 14.25V1.75Zm1.75-.25a.25.25 0 0 0-.25.25v12.5c0 .138.112.25.25.25h9.5a.25.25 0 0 0 .25-.25V6h-2.75A1.75 1.75 0 0 1 9 4.25V1.5H3.75Zm6.75.062V4.25c0 .138.112.25.25.25h2.688l-2.938-2.938Z"/></svg>'
            html += f'<div class="file-item">\n<div class="file-title">{svg_file} <a href="{rel_path}">{display_name}</a></div>\n{tags_html}\n</div>\n'
        html += '</div>\n'
    return html

tree_html = f'<div class="directory-wrapper">\n{build_html_tree(target_dir, target_dir)}</div>\n'
dir_name = os.path.basename(os.path.abspath(target_dir)) or "Root"

final_html = template_content.replace("#&--TITLE_NAME--&#", f"{dir_name} - 知识库索引")
final_html = final_html.replace("#&--HEAD_NAME--&#", f"{dir_name} Index")
final_html = final_html.replace("#&--HEAD_PATH--&#", f"/{dir_name}/index.html")
final_html = final_html.replace("#&--START--&#", tree_html)

output_file = os.path.join(target_dir, "index.html")
with open(output_file, "w+", encoding="utf-8") as f:
    f.write(final_html)

print(f"🎉 成功生成知识库目录索引页: {output_file}")