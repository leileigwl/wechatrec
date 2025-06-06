# WeChat Article Search Frontend

这是微信文章搜索系统的前端部分，提供了一个类似Google的搜索界面，用于搜索和展示微信公众号文章。

## 功能特点

- 简洁的搜索界面，类似Google
- 响应式设计，适配各种屏幕尺寸
- 分页浏览搜索结果
- 显示文章标题、摘要、封面图片、公众号名称和发布日期
- 支持URL参数，便于分享搜索结果

## 文件结构

```
frontend/
├── css/
│   └── styles.css       # 样式文件
├── js/
│   └── search.js        # 搜索功能JavaScript
├── img/
│   ├── logo.svg         # 网站Logo
│   └── favicon.svg      # 网站图标
└── index.html           # 主页HTML
```

## 部署说明

### 本地开发

可以使用任何HTTP服务器在本地提供服务，例如：

```bash
# 使用Python的HTTP服务器
python -m http.server 8080

# 或使用Node.js的http-server
npx http-server -p 8080
```

然后在浏览器中访问 `http://localhost:8080`

### 生产环境

在生产环境中，您可以：

1. 将前端文件部署到任何静态文件服务器
2. 或者将前端文件放在后端服务的静态文件目录中

## API集成

前端默认连接到 `http://localhost:8000` 的后端API。如需更改API地址，请修改 `js/search.js` 文件中的 `API_URL` 常量。

API调用格式：

```
GET /search/?q={查询关键词}&page={页码}&size={每页结果数}
```

## 浏览器兼容性

- Chrome 60+
- Firefox 60+
- Safari 12+
- Edge 79+

## 自定义

- 要更改搜索结果的显示方式，请修改 `index.html` 中的结果模板和 `search.js` 中的 `displaySearchResults` 函数
- 要更改样式，请修改 `css/styles.css` 文件
- 要更改Logo，请替换 `img/logo.svg` 文件 