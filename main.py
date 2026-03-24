import pathlib as Path
import sys
from tools import printInfo,info_type
from dataclasses import dataclass
from enum import Enum
import re
import markdown
import html
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound

#读取模板文件
template_filename=sys.argv[2]

try:
    with open(f"{template_filename}.html","r",encoding="utf-8") as f:
       template_content=f.readlines()
except FileNotFoundError:
    printInfo(info_type.ERROR,f"指定路径没有找到{template_filename}.html")
    sys.exit(100)
except PermissionError:
    printInfo(info_type.ERROR,f"没有打开{template_filename}.html的权限")
    sys.exit(101)
except Exception as e:
    printInfo(info_type.ERROR,f"打开{template_filename}.html时发生异常，错误原因：{type(e)}")
    sys.exit(102)

class pin_pair:
    def __init__(self,name,value):
        self.__pin_name=name
        self.__pin_value=value
    def getName(self):
        return self.__pin_name
    def getValue(self):
        return self.__pin_value

#读取替换标记文件并存储处理后的数据
pins:list[pin_pair]=[]

try:
    with open(f"{template_filename}.pin","r",encoding="utf-8") as fp:
        fp_content=fp.readlines()
        for i in range(len(fp_content)):
            pair=fp_content[i].split(" ")
            if len(pair)==2:
                pin_name=pair[0]
                try:
                    pin_value=int(pair[1])
                except ValueError:
                    printInfo(info_type.WARNING,f"无法转换{template_filename}.pin第{i+1}行的标记，请检查标记行号是否为整数")
                    continue
                except Exception as e:
                    printInfo(info_type.WARNING,f"无法转换{template_filename}.pin第{i+1}行的标记，错误原因：{type(e)}")
                    continue
            pins.append(pin_pair(pin_name,pin_value))
except FileNotFoundError:
    pass
except PermissionError:
    printInfo(info_type.WARNING,f"没有打开{template_filename}.pin的权限，跳过读取")
except Exception as e:
    printInfo(info_type.WARNING,f"打开{template_filename}.pin时发生异常跳过，错误原因：{type(e)}")

#pins.sort(key=lambda s:s.getValue())

#读入并格式化md文件文件名（不带扩展名）
filename=sys.argv[1]
if filename.endswith(".md"):
    temp=filename.split(".")
    temp.pop(-1)
    filename=""
    for t in temp:
        filename+=t

#读取要转换的文件并将内容存入内存
try:
    with open(f"{filename}.md","r",encoding="utf-8") as original_file:
        markdown_content=original_file.read()
except FileNotFoundError:
    printInfo(info_type.ERROR,f"指定路径没有找到{filename}.md")
    sys.exit(100)
except PermissionError:
    printInfo(info_type.ERROR,f"没有打开{filename}.md的权限")
    sys.exit(101)
except Exception as e:
    printInfo(info_type.ERROR,f"打开{filename}.md时发生异常，错误原因：{type(e)}")
    sys.exit(102)

formatter = HtmlFormatter(style='dracula', cssclass="source-code", nobackground=True)
highlight_css = formatter.get_style_defs('.source-code')

#寻找入口标记并进行模板信息替换
start_pin=-1
for i in range(len(template_content)):
    if "#&--START--&#" in template_content[i]:
        start_pin = i
    if "#&--" in template_content[i]:
        template_content[i] = template_content[i].replace("#&--TITLE_NAME--&#", filename)
        template_content[i] = template_content[i].replace("#&--SYNTAX_CSS--&#", highlight_css)
        template_content[i] = template_content[i].replace("#&--HEAD_NAME--&#", filename)
        template_content[i] = template_content[i].replace("#&--HEAD_PATH--&#", f"NoteBook/{filename}.md")

if start_pin == -1:
    printInfo(info_type.ERROR,f"未在模板文件中找到入口标记(#&--START--&#)，请检查模板文件并重试")
    sys.exit()

#转换

def render_code_block(match) -> str:
    """
    当正则匹配到 ```语言...``` 时触发的逻辑
    """
    lang = match.group(1).strip() if match.group(1) else "text"
    #print(f"DEBUG: 正在处理语言为 {lang} 的代码块")
    code = match.group(2)

    try:
        # 尝试根据 ``` 后面的标识获取词法分析器（如 'cpp', 'python'）
        lexer = get_lexer_by_name(lang, stripall=True)
    except ClassNotFound:
        # 优化方案：健壮性容错
        # 如果用户写了 ```unknown 或者库不支持该语言，优雅降级为纯文本
        lexer = get_lexer_by_name("text", stripall=True)

    # 配置 HTML 格式化器
    # cssclass="source-code" 表示最外层包裹的 div 的类名，用于 CSS 隔离
    formatter = HtmlFormatter(linenos=True, cssclass="source-code", nobackground=True)
    
    highlighted = highlight(code, lexer, formatter)
    escaped_code = html.escape(code)
    svg_copy = '<svg class="icon-copy" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M4 1.5H3a2 2 0 0 0-2 2V14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V3.5a2 2 0 0 0-2-2h-1v1h1a1 1 0 0 1 1 1V14a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V3.5a1 1 0 0 1 1-1h1v-1z"/><path d="M9.5 1h-3a.5.5 0 0 0-.5.5v1a.5.5 0 0 0 .5.5h3a.5.5 0 0 0 .5-.5v-1a.5.5 0 0 0-.5-.5z"/></svg>'
    svg_check = '<svg class="icon-check" style="display: none; color: #4caf50;" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M10.97 4.97a.75.75 0 0 1 1.07 1.05l-3.99 4.99a.75.75 0 0 1-1.08.02L4.324 8.384a.75.75 0 1 1 1.06-1.06l2.094 2.093 3.473-4.425a.267.267 0 0 1 .02-.022z"/></svg>'
    
    wrapper = f'''<div class="code-block-wrapper" style="position: relative;">
    <button class="copy-button" data-code="{escaped_code}" style="position: absolute; top: 8px; right: 8px; background: transparent; border: none; cursor: pointer; color: #888;" title="复制" onclick="copyCode(this)">
        {svg_copy}{svg_check}
    </button>
    {highlighted}</div>'''
    return wrapper

def parse_markdown_with_lib(md_text: str) -> str:
    meta_html = ""
    # 匹配 YAML 区块
    meta_match = re.search(r'^---\s*\n(.*?)\n---\s*\n', md_text, re.DOTALL)
    
    if meta_match:
        raw_meta = meta_match.group(1)
        md_text = md_text[meta_match.end():] 
        
        meta_html = '<div class="metadata-panel">'
        lines = raw_meta.split('\n')
        
        for line in lines:
            line_strip = line.strip()
            if not line_strip: continue
            
            # 情况 A: 处理 key: value
            if ':' in line_strip and not line_strip.startswith('-'):
                key, value = line_strip.split(':', 1)
                val = value.strip()
                if "http" in val:
                    display_val = val if len(val) <= 50 else val[:47] + "..."
                    val = f'<a href="{val}" target="_blank">{display_val}</a>'
                
                # 如果 value 为空，说明下面跟着列表项，我们先只放 Key
                meta_html += f'<div class="meta-item"><span class="meta-key">{key.strip()}</span>'
                if val:
                    meta_html += f'<span class="meta-value">{val}</span>'
                meta_html += '</div>'
                
            # 情况 B: 处理列表项 - xxx
            elif line_strip.startswith('-'):
                tag_content = line_strip[1:].strip()
                # 将列表项包装成漂亮的小标签，插入到上一个 meta-item 中
                # 我们利用 CSS 的灵活性，直接在后面追加 tag 标签
                meta_html = meta_html[:-6] # 移除上一个 </div> 标签
                meta_html += f'<span class="meta-tag">{tag_content}</span>&nbsp;</div>'
                
        meta_html += '</div>'

    # 1. 提取并渲染代码块（优先提取，防止其中的 $ 符号被误认为公式）
    code_blocks = []
    html = re.sub(r'```(\w*)\n(.*?)```', lambda m: f'HTMLExtractCodeBlock{code_blocks.append(render_code_block(m)) or len(code_blocks)-1}EndExtract', md_text, flags=re.DOTALL)

    # 2. 提取公式块（避免被 markdown 引擎错误解析内部的下划线等为斜体）
    math_blocks = []
    html = re.sub(r'\$\$([^$]+?)\$\$', lambda m: f'HTMLExtractMathBlock{math_blocks.append(m.group(1)) or len(math_blocks)-1}EndExtract', html, flags=re.DOTALL)
    math_inlines = []
    html = re.sub(r'\$([^\n$]+?)\$', lambda m: f'HTMLExtractMathInline{math_inlines.append(m.group(1)) or len(math_inlines)-1}EndExtract', html)

    # 1. 核心修改：将 ![[filename.png]] 转换为 HTML <img> 标签
    # 这里的 src 先填入文件名作为占位符，后期你可以根据图床规则批量替换路径
    html = re.sub(r'!\[\[(.*?)\.(.*?)\]\]', r'<div class="img-wrapper"><img src="\1.\2" alt="\1"></div>', html)

    # 2. 原有逻辑：处理标准 Markdown 图片 ![alt](url)
    # 如果你手动改了部分链接为图床地址，这行也能兼容
    html = re.sub(r'!\[(.*?)\]\((.*?)\)', r'<div class="img-wrapper"><img src="\2" alt="\1"></div>', html)

    # ... 后续调用 markdown.markdown(md_text, ...) 以及其他替换逻辑

    html = markdown.markdown(html, extensions=['fenced_code', 'tables'])
    
    html = re.sub(r'==(.*?)==', r'<mark>\1</mark>', html)
    html = re.sub(r'\[\[(.*?)\|(.*?)\]\]', r'<a href="\1">\2</a>', html)
    
    # 3. 还原代码块和公式
    for i, code_html in enumerate(code_blocks):
        # 抹除 markdown 引擎自动为占位符添加的 <p> 标签
        html = html.replace(f'<p>HTMLExtractCodeBlock{i}EndExtract</p>', code_html)
        html = html.replace(f'HTMLExtractCodeBlock{i}EndExtract', code_html)
    for i, math_code in enumerate(math_blocks):
        html = html.replace(f'HTMLExtractMathBlock{i}EndExtract', f'$${math_code}$$')
    for i, math_code in enumerate(math_inlines):
        html = html.replace(f'HTMLExtractMathInline{i}EndExtract', f'${math_code}$')

    js_script = """
<script>
window.MathJax = {
  tex: {
    inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
    displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']]
  }
};
</script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
<script>
function copyCode(btn) {
    const codeText = btn.getAttribute('data-code');
    navigator.clipboard.writeText(codeText).then(() => {
        const iconCopy = btn.querySelector('.icon-copy');
        const iconCheck = btn.querySelector('.icon-check');
        iconCopy.style.display = 'none';
        iconCheck.style.display = 'inline-block';
        btn.addEventListener('mouseleave', function onMouseLeave() {
            iconCopy.style.display = 'inline-block';
            iconCheck.style.display = 'none';
            btn.removeEventListener('mouseleave', onMouseLeave);
        });
    });
}
</script>
"""
    return meta_html+html+js_script
try:
    with open(f"{filename}.html","w+",encoding="utf-8") as f:
        f.writelines(template_content[0:start_pin])
        f.write(parse_markdown_with_lib(markdown_content))
        f.writelines(template_content[start_pin+1:])
except PermissionError:
    printInfo(info_type.ERROR,f"没有创建或访问{filename}.html的权限")
    sys.exit(201)
except FileExistsError:
    printInfo(info_type.ERROR,f"{filename}.html已存在且覆盖请求被拒绝")
    sys.exit(202)
except Exception as e:
    printInfo(info_type.ERROR,f"打开{filename}.html时发生异常，错误原因：{type(e)}")
    sys.exit(200)