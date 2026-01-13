# 依框架分類的 CLAUDE.md 模板

> 針對熱門框架和技術棧的即用型 CLAUDE.md 模板。

## 如何使用這些模板

1. 複製適合你技術棧的模板
2. 貼到專案根目錄的 `CLAUDE.md`
3. 自訂括號內的 `[佔位符]`
4. 移除不適用的章節
5. 新增專案特定規則

## 模板

### React + TypeScript

```markdown
# [專案名稱]

## 技術棧
- React 18+ with TypeScript
- [狀態管理: Redux Toolkit / Zustand / Context]
- [樣式: Tailwind CSS / styled-components / CSS Modules]
- [測試: Vitest / Jest + React Testing Library]

## 專案結構
```
src/
├── components/     # 可重用 UI 元件
├── pages/          # 路由元件
├── hooks/          # 自訂 React hooks
├── store/          # 狀態管理
├── services/       # API 呼叫
├── types/          # TypeScript 型別
└── utils/          # 工具函式
```

## 程式碼規範

### 元件
- 僅使用函式元件（不用 class 元件）
- Props 介面定義在元件上方
- 使用 `const Component: React.FC<Props>` 模式
- 元件、樣式、測試放在一起

### 命名
- 元件：PascalCase (`UserProfile.tsx`)
- Hooks：camelCase 加 `use` 前綴 (`useAuth.ts`)
- 工具：camelCase (`formatDate.ts`)
- 型別：PascalCase 加描述性後綴 (`UserResponse`)

### 狀態管理
- 本地 state 用於純 UI 狀態
- 全域 state 用於共享資料
- Server state 使用 [React Query / SWR]

## 測試
- 執行測試：`npm test`
- 覆蓋率目標：80%
- 測試使用者行為，而非實作細節

## 指令
```bash
npm run dev      # 開發伺服器
npm run build    # 正式環境建置
npm run test     # 執行測試
npm run lint     # Lint 檢查
```
```

---

### Next.js 14+ (App Router)

```markdown
# [專案名稱]

## 技術棧
- Next.js 14+ with App Router
- TypeScript strict mode
- [資料庫: Prisma / Drizzle + PostgreSQL]
- [驗證: NextAuth.js / Clerk]
- Tailwind CSS

## 專案結構
```
app/
├── (auth)/         # 驗證路由群組
├── (dashboard)/    # Dashboard 路由群組
├── api/            # API 路由
└── layout.tsx      # 根 layout

components/
├── ui/             # Shadcn/ui 元件
└── features/       # 功能元件

lib/
├── db.ts           # 資料庫客戶端
├── auth.ts         # 驗證工具
└── utils.ts        # 工具函式
```

## 程式碼規範

### Server vs Client Components
- 預設使用 Server Components
- 僅在需要時加 'use client'（hooks、瀏覽器 APIs）
- Client components 保持小巧且在葉節點

### 資料獲取
- Server Components：直接呼叫資料庫/API
- Client Components：Server Actions 或 API routes
- 務必處理 loading 和 error 狀態

### Route Handlers
- 使用 `route.ts` 作為 API 端點
- 回傳 JSON 使用 `NextResponse.json()`
- 用適當的狀態碼處理錯誤

## 資料庫
- 遷移：`npx prisma migrate dev`
- 產生：`npx prisma generate`
- Studio：`npx prisma studio`

## 指令
```bash
npm run dev      # 開發（turbopack）
npm run build    # 正式環境建置
npm run start    # 正式環境伺服器
npm run lint     # ESLint 檢查
```

## 環境變數
`.env.local` 必要項目：
- `DATABASE_URL`
- `NEXTAUTH_SECRET`
- `NEXTAUTH_URL`
```

---

### Python + FastAPI

```markdown
# [專案名稱]

## 技術棧
- Python 3.11+
- FastAPI with Pydantic v2
- SQLAlchemy 2.0 + PostgreSQL
- Alembic 遷移
- pytest 測試

## 專案結構
```
app/
├── api/
│   ├── routes/      # API 端點
│   └── deps.py      # 依賴項
├── core/
│   ├── config.py    # 設定
│   └── security.py  # 驗證工具
├── models/          # SQLAlchemy models
├── schemas/         # Pydantic schemas
├── services/        # 商業邏輯
└── main.py          # App 進入點

tests/
├── api/             # API 測試
├── services/        # Service 測試
└── conftest.py      # Fixtures
```

## 程式碼規範

### 型別提示
- 所有函式必須有型別提示
- 使用 Pydantic models 處理 request/response
- 避免使用 `Any` 型別

### API 設計
- 使用正確的 HTTP 方法（GET、POST、PUT、DELETE）
- 回傳適當的狀態碼
- 使用依賴注入處理 auth、db

### 資料庫
- 使用 async SQLAlchemy
- 每個檔案一個 model
- 所有 schema 變更使用 Alembic

## 指令
```bash
# 開發
uvicorn app.main:app --reload

# 測試
pytest -v
pytest --cov=app

# 資料庫
alembic upgrade head
alembic revision --autogenerate -m "description"

# Linting
ruff check .
mypy app/
```

## 環境變數
`.env` 必要項目：
- `DATABASE_URL`
- `SECRET_KEY`
- `ENVIRONMENT` (development/production)
```

---

### Node.js + Express + TypeScript

```markdown
# [專案名稱]

## 技術棧
- Node.js 20+ with TypeScript
- Express.js
- [資料庫: Prisma / TypeORM + PostgreSQL]
- Jest 測試
- Zod 驗證

## 專案結構
```
src/
├── controllers/     # 請求處理器
├── services/        # 商業邏輯
├── models/          # 資料庫 models
├── middleware/      # Express middleware
├── routes/          # 路由定義
├── utils/           # 工具函式
├── types/           # TypeScript 型別
└── app.ts           # Express app 設定

tests/
├── integration/     # API 測試
└── unit/            # 單元測試
```

## 程式碼規範

### 錯誤處理
- 使用自訂錯誤類別
- 集中式錯誤 middleware
- 永不對客戶端暴露內部錯誤

### 驗證
- 所有輸入用 Zod 驗證
- 清理使用者輸入
- 驗證錯誤回傳 400

### 身份驗證
- JWT 存在 httpOnly cookies
- Refresh token 輪換
- Auth 端點限流

## API 回應格式
```typescript
// 成功
{ "data": {...}, "meta": {...} }

// 錯誤
{ "error": { "code": "...", "message": "..." } }
```

## 指令
```bash
npm run dev      # 使用 nodemon 開發
npm run build    # 編譯 TypeScript
npm run start    # 正式環境伺服器
npm run test     # 執行測試
npm run lint     # ESLint 檢查
```

## 環境變數
`.env` 必要項目：
- `PORT`
- `DATABASE_URL`
- `JWT_SECRET`
- `NODE_ENV`
```

---

### Go + Gin/Echo

```markdown
# [專案名稱]

## 技術棧
- Go 1.21+
- [框架: Gin / Echo]
- PostgreSQL with pgx
- golang-migrate 遷移
- testify 測試

## 專案結構
```
cmd/
└── api/
    └── main.go      # 進入點

internal/
├── handler/         # HTTP handlers
├── service/         # 商業邏輯
├── repository/      # 資料庫存取
├── model/           # 領域 models
├── middleware/      # HTTP middleware
└── config/          # 設定

pkg/
└── utils/           # 共用工具

migrations/          # SQL 遷移
```

## 程式碼規範

### 錯誤處理
- 回傳錯誤，不要 panic
- 包裝錯誤加上 context
- 使用自訂錯誤型別處理領域錯誤

### 命名
- Packages：小寫，單字
- Interfaces：動詞-er 模式 (`Reader`、`Handler`)
- 避免重複 (`user.User` → `user.Model`)

### 資料庫
- 使用 prepared statements
- 設定連線池
- 多步驟操作使用 transactions

## 指令
```bash
# 開發
go run cmd/api/main.go

# 建置
go build -o bin/api cmd/api/main.go

# 測試
go test ./...
go test -cover ./...

# 遷移
migrate -path migrations -database $DATABASE_URL up
migrate -path migrations -database $DATABASE_URL down 1
```

## 環境變數
必要項目：
- `PORT`
- `DATABASE_URL`
- `JWT_SECRET`
- `ENVIRONMENT`
```

---

### Vue 3 + TypeScript

```markdown
# [專案名稱]

## 技術棧
- Vue 3 with Composition API
- TypeScript
- [狀態: Pinia]
- [路由: Vue Router 4]
- [UI: Vuetify / PrimeVue / Naive UI]
- Vite

## 專案結構
```
src/
├── components/      # 可重用元件
├── views/           # 路由 views
├── composables/     # Composition 函式
├── stores/          # Pinia stores
├── services/        # API services
├── types/           # TypeScript 型別
├── utils/           # 工具函式
└── router/          # 路由定義
```

## 程式碼規範

### 元件
- 使用 `<script setup lang="ts">`
- Props 使用 TypeScript interfaces
- Emit 使用型別化事件
- 單檔案元件 (.vue)

### Composition API
- 基本型別使用 `ref`，物件使用 `reactive`
- 將邏輯抽取到 composables
- Composables 命名使用 `use` 前綴

### 狀態管理
- Pinia 處理全域狀態
- 使用 `defineStore` 定義 stores
- 使用 getters 處理計算狀態

## 指令
```bash
npm run dev      # 開發伺服器
npm run build    # 正式環境建置
npm run preview  # 預覽正式環境
npm run test     # 執行測試
npm run lint     # Lint 檢查
```
```

---

### Astro + React/Vue

```markdown
# [專案名稱]

## 技術棧
- Astro 4+
- [UI 框架: React / Vue / Svelte]
- Tailwind CSS
- [CMS: Contentful / Sanity / MDX]

## 專案結構
```
src/
├── components/      # UI 元件
├── layouts/         # 頁面 layouts
├── pages/           # 檔案式路由
├── content/         # Content collections
├── styles/          # 全域樣式
└── utils/           # 工具函式

public/              # 靜態資源
```

## 程式碼規範

### Islands 架構
- 預設靜態（無 JS）
- 僅在需要時加 `client:*`
- 折疊下方內容優先使用 `client:visible`

### Content Collections
- 在 `src/content/config.ts` 定義 schemas
- 使用型別安全查詢
- 驗證 frontmatter

### 效能
- 最小化 client-side JS
- 使用圖片最佳化
- 預載關鍵資源

## 指令
```bash
npm run dev      # 開發伺服器
npm run build    # 正式環境建置
npm run preview  # 預覽正式環境
astro add [pkg]  # 新增整合
```
```

---

### Django + DRF

```markdown
# [專案名稱]

## 技術棧
- Python 3.11+ / Django 5+
- Django REST Framework
- PostgreSQL
- Celery + Redis（背景任務）
- pytest-django

## 專案結構
```
project/
├── config/          # Django 設定
│   ├── settings/
│   │   ├── base.py
│   │   ├── local.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── users/       # User app
│   ├── core/        # 共用工具
│   └── [feature]/   # 功能 apps
├── tests/           # 測試檔案
└── manage.py

```

## 程式碼規範

### Apps
- 每個領域概念一個 app
- 保持 apps 小巧專注
- 所有 apps 使用 apps/ 目錄

### Models
- 主鍵使用 UUIDs
- 新增 `created_at`、`updated_at` 時間戳
- 為所有 models 定義 `__str__`

### API
- CRUD 使用 ViewSets
- 自訂 actions 使用 `@action` 裝飾器
- 所有列表端點加分頁

### Serializers
- 需要時分開 read/write serializers
- 在 serializer 驗證，不在 view
- 謹慎使用 `SerializerMethodField`

## 指令
```bash
# 開發
python manage.py runserver

# 資料庫
python manage.py makemigrations
python manage.py migrate

# 測試
pytest
pytest --cov=apps

# Shell
python manage.py shell_plus
```

## 環境變數
必要項目：
- `SECRET_KEY`
- `DATABASE_URL`
- `REDIS_URL`
- `DJANGO_SETTINGS_MODULE`
```

---

### Ruby on Rails

```markdown
# [專案名稱]

## 技術棧
- Ruby 3.2+ / Rails 7+
- PostgreSQL
- [前端: Hotwire / React]
- RSpec + FactoryBot
- Sidekiq 背景任務

## 專案結構
```
app/
├── controllers/
├── models/
├── views/
├── services/        # Service objects
├── queries/         # Query objects
└── jobs/            # 背景任務

spec/
├── models/
├── requests/
├── services/
└── factories/
```

## 程式碼規範

### Controllers
- 精簡 controllers，肥胖 models
- 使用 `before_action` 處理 auth
- 回應適當的狀態碼

### Models
- 驗證放在 model
- 常見查詢使用 scopes
- Callbacks 謹慎使用（優先使用 service objects）

### Service Objects
- 一個公開方法（`call`）
- 回傳 Result 物件或拋出例外
- 盡可能無副作用

## 指令
```bash
# 開發
bin/rails server

# 資料庫
bin/rails db:migrate
bin/rails db:seed

# 測試
bundle exec rspec
bundle exec rspec --format documentation

# Console
bin/rails console

# 產生
bin/rails generate model User name:string email:string
```

## 環境變數
`.env` 必要項目：
- `DATABASE_URL`
- `REDIS_URL`
- `SECRET_KEY_BASE`
- `RAILS_ENV`
```

---

## 自訂技巧

### 新增專案特定章節

```markdown
## 商業邏輯

### [領域概念]
- 規則 1
- 規則 2

### 工作流程
1. 步驟 1
2. 步驟 2
```

### 新增團隊慣例

```markdown
## 團隊慣例

### Code Review
- 所有 PRs 需要 1 個核准
- 使用 conventional commits
- Squash merge 到 main

### 分支命名
- feature/[ticket]-description
- fix/[ticket]-description
- chore/description
```

### 新增外部服務

```markdown
## 外部服務

### [服務名稱]
- 用途：[為何使用]
- Dashboard：[URL]
- 文件：[URL]
```

## 總結

1. **從模板開始** - 不要從頭寫
2. **為專案自訂** - 移除不適用的部分
3. **保持更新** - CLAUDE.md 是活文件
4. **具體明確** - 模糊指示 = 不一致結果
5. **包含指令** - Claude 需要知道如何執行

---

另見：[CLAUDE.md 原則](../../concepts/claude-md-principles.md) | [CLAUDE.md 反模式](../../concepts/claude-md-anti-patterns.md)
