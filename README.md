## Power_Forecast

基于 Django 后端与 Vite + Vue3 前端的新能源场站功率预测与可视化平台。提供表结构检查、场站与气象/功率数据管理、预测任务管理，以及基于 CSV 的功率预测可视化仪表板。

### 技术栈
- 后端：Django 4.x（PostgreSQL 数据库）
- 前端：Vite + Vue 3 + Element Plus + ECharts/Chart.js
- 其他：Pandas（CSV 数据分析）、AMap JS API（可视化地图，若使用）

### 目录结构（关键）
```
Power_Forecast/
├─ manage.py
├─ Power_Forecast/                # Django 项目（settings/urls/wsgi 等）
│  ├─ settings.py                 # PostgreSQL 连接、模板路径、语言/时区
│  ├─ urls.py                     # 根路由，包含 list_tables 应用
│  └─ templates/                  # 顶层模板（dashboard/list_tables 等）
├─ list_tables/                   # 核心应用：接口与页面
│  ├─ models.py                   # 站点/气象/功率/任务等模型
│  ├─ views.py                    # REST 风格接口与 CSV 可视化 API
│  ├─ urls.py                     # /api/... 接口与页面路由
│  └─ templates/power_visualization/dashboard.html
├─ frontend/                      # Vite + Vue3 前端（端口 5174）
│  ├─ package.json                # dev/build/preview 脚本
│  ├─ vite.config.js              # 本地代理至后端 http://localhost:8000
│  └─ src/                        # 组件与页面
├─ media/                         # CSV 数据（*_results.csv 等）
└─ package.json                   # 根级前端依赖（Chart.js/Element Plus/Leaflet）
```

### 环境准备
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+（本地或远程均可）

### 数据库配置
在 `Power_Forecast/settings.py` 中默认配置如下（请按需修改）：
```
DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': 'dachuang',
    'USER': 'postgres',
    'PASSWORD': '12345678',
    'HOST': 'localhost',
    'PORT': '5432',
  }
}
```
注意：生产环境请设置安全的 `SECRET_KEY`、`ALLOWED_HOSTS` 与 `DEBUG=False`。

### 后端启动（Django）
1) 进入项目根目录并创建虚拟环境（可选）：
```
python -m venv .venv
.venv\Scripts\activate
```
2) 安装依赖（如有 `requirements.txt` 则优先使用；否则确保安装 Django、psycopg2、pandas 等）：
```
pip install django psycopg2-binary pandas
```
3) 迁移数据库并启动服务：
```
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```
4) 验证接口：
- 浏览器打开 `http://localhost:8000/`（根路由已包含 `list_tables.urls`）
- 列表页：`/api/list`

### 前端启动（Vite + Vue3）
1) 切换到前端目录：
```
cd frontend
```
2) 安装依赖并启动：
```
npm install
npm run dev
```
3) 访问 `http://localhost:5174/`

代理说明：`frontend/vite.config.js` 已将以 `/tables` 开头的请求代理到 `http://localhost:8000`。若需要代理 `/api` 路径，请在该文件中补充对应代理规则。

### 主要接口与页面
- 页面
  - `GET /power-dashboard/`：功率预测可视化仪表板（基于 `media/*.csv`）
  - `GET /core-function/`：核心功能展示页
  - `GET /api/list`：数据库表列表页

- 场站与结构
  - `GET /api/stations/` 列表，`POST /api/stations/` 新建
  - `GET /api/stations/<id>/` 详情，`PUT/DELETE` 更新/删除
  - `GET /api/check-structure/` 表结构检查

- 预测任务与功率/气象数据
  - `GET/POST /api/tasks/`，`GET/PUT/DELETE /api/tasks/<id>/`
  - `GET/POST /api/power-data/`
  - `GET/POST /api/weather-data1/`
  - `GET/POST /api/weather-data2/`

- CSV 可视化 API（默认读取 `media/新乐凤鸣光伏电站_results.csv`，可按需调整 `views.py` 中路径）
  - `GET /api/wind-power-data/`
  - `GET /api/daily-power-stats/`
  - `GET /api/power-comparison/`

示例：
```
GET /api/wind-power-data/?start_date=2024-01-01&end_date=2024-01-31
```

### 开发注意事项
- 模板路径：`settings.py` 中 `TEMPLATES['DIRS'] = [BASE_DIR / 'templates']`
- 时区/语言：`LANGUAGE_CODE = 'zh-hans'`，`TIME_ZONE = 'Asia/Shanghai'`
- CSV 路径：`MEDIA_ROOT` 下的 `*_results.csv`，不存在将返回 404
- 根路由：`Power_Forecast/urls.py` 中包含 `path('', include('list_tables.urls'))`

### 常见问题（FAQ）
- 接口 403：`/api/logs/` 需要管理员用户（`is_staff`）。
- 连接数据库失败：检查 PostgreSQL 连接信息与网络可达性；本地需启动服务且创建数据库 `dachuang`。
- CSV 未找到：确认 `media/` 目录下是否存在对应 `*_results.csv` 文件，或在 `views.py` 中修改路径。
- CORS/跨域：通过 Vite 代理或配置 Django 中间件（生产环境建议 Nginx 反向代理）。

### 许可证
若无特别说明，默认此项目仅用于教学与研究目的。


