# MarkdownToHTML

在AI的协助下开发的一个将markdown文件转换为HTML的工具

## 食用方式：

虽然估计没人看，但还是写一下吧（默认为Linux，Windows也能用）～

首先克隆仓库并进入目录：

```
git clone https://github.com/Leumc/MarkdownToHTML.git
cd MarkdownToHTML
```

然后创建并激活虚拟环境（Windows请跳过这一步）：

```
python3 -m venv .venv
source .venv/bin/activate
```

安装依赖：

```
pip install -r requirements.txt
```

运行主程序并指定需要转换的文件和模板文件：

```
python3 main.py [文件路径] [模板名（没有扩展名）]
```
## 关于模板：

项目提供了一个模板文件`template.html`，是[我的笔记页面](https://github.com/Leumc/NoteBook)使用的模板（Gemini设计的）。

如果你想整一个自己的模板，这里有一些你应该知道的信息：

模板使用`#&--XXX---&#`作为标记来，目前有的标记如下（如果要修改替换逻辑，请修改`main.py`第62行及以下的对应内容）：

1. `#&--START--&#`：必不可少的标记，程序会将这个标记替换为转换后的正文，缺少这个标记程序将无法运行！
2. `#&--TITLE_NAME--&#`/`#&--HEAD_NAME--&#`：这个标记会被替换为转换文件的文件名（没有扩展名）。
3. `#&--SYNTAX_CSS--&#`：你不需要处理代码块的高亮显示，只需要把这个标记放在`<style>`标签中的某处即可，程序会在这里插入高亮样式。如果需要修改风格，可以修改`main.py`第53行中传入`HtmlFormatter`的`style`参数。
4. `#&--HEAD_PATH--&#`：这个标记会被默认替换为`NoteBook/文件名.md`。
## 关于[不蒜子](https://www.busuanzi.cc/)：

项目提供的模板文件会默认使用[不蒜子](https://www.busuanzi.cc/)提供的网站访客计数服务，在预览模式（比如`VS Code`的预览插件或者浏览器访问本地文件）显示的访客数据是[不蒜子](https://www.busuanzi.cc/)主站的数据。

该服务是根据网站的`url`来进行计数的，如果需要正确的访客数据，请使用域名访问页面（`IP+端口`访问也会显示[不蒜子](https://www.busuanzi.cc/)主站的数据）。

具体详见[不蒜子官方文档](https://www.busuanzi.cc/doc.php)。