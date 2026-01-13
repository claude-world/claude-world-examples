# 重構與程式碼品質模式

> 讓 Claude 作為你的重構夥伴，系統性地改善程式碼。

## 為什麼要用 Claude 重構？

重構是：
- **有風險的** - 容易破壞功能
- **耗時的** - 很多檔案要修改
- **繁瑣的** - 重複的模式

Claude 擅長：
- 識別重構機會
- 跨檔案進行一致的變更
- 確保測試仍然通過
- 記錄變更內容

## 重構工作流程

### 步驟 1: 識別機會

```
「分析這個程式碼庫的重構機會：
- 過長的函式（>50 行）
- 重複的程式碼
- 深層巢狀（>3 層）
- 複雜的條件判斷
- 大型檔案（>500 行）」
```

Claude 回傳優先順序清單，包含位置和建議修復。

### 步驟 2: 規劃重構

```
「為 [特定問題] 建立重構計畫：
- 需要哪些變更
- 影響哪些檔案
- 哪些測試需要更新
- 風險評估」
```

### 步驟 3: 執行並測試

```
「按照計畫重構 [特定函式/模組]。
確保每次變更後所有測試通過。」
```

### 步驟 4: 驗證和記錄

```
「驗證重構完成：
- 所有測試通過
- 功能沒有改變
- 程式碼指標改善
- 變更已記錄」
```

## 常見重構模式

### 1. 提取函式

**之前**：
```javascript
async function processOrder(order) {
  // 50 行驗證
  if (!order.items) throw new Error('No items');
  if (order.items.length === 0) throw new Error('Empty order');
  for (const item of order.items) {
    if (!item.productId) throw new Error('Missing product ID');
    if (!item.quantity || item.quantity < 1) throw new Error('Invalid quantity');
    const product = await getProduct(item.productId);
    if (!product) throw new Error('Product not found');
    if (product.stock < item.quantity) throw new Error('Insufficient stock');
  }

  // 30 行計算
  let subtotal = 0;
  for (const item of order.items) {
    const product = await getProduct(item.productId);
    subtotal += product.price * item.quantity;
  }
  const tax = subtotal * 0.1;
  const shipping = subtotal > 100 ? 0 : 10;
  const total = subtotal + tax + shipping;

  // 20 行儲存
  // ...
}
```

**Claude 指令**：
```
「透過提取以下函式重構 processOrder：
- validateOrder 函式
- calculateTotals 函式
- saveOrder 函式」
```

**之後**：
```javascript
async function processOrder(order) {
  await validateOrder(order);
  const totals = await calculateTotals(order);
  return await saveOrder(order, totals);
}

async function validateOrder(order) {
  if (!order.items?.length) {
    throw new ValidationError('Order must have items');
  }
  await Promise.all(order.items.map(validateItem));
}

async function calculateTotals(order) {
  const subtotal = await calculateSubtotal(order.items);
  const tax = subtotal * TAX_RATE;
  const shipping = subtotal > FREE_SHIPPING_THRESHOLD ? 0 : SHIPPING_COST;
  return { subtotal, tax, shipping, total: subtotal + tax + shipping };
}
```

### 2. 用多型取代條件判斷

**之前**：
```javascript
function calculateDiscount(customer, amount) {
  if (customer.type === 'regular') {
    return amount * 0.05;
  } else if (customer.type === 'premium') {
    return amount * 0.10;
  } else if (customer.type === 'vip') {
    return amount * 0.15 + 10;
  } else if (customer.type === 'employee') {
    return amount * 0.25;
  }
  return 0;
}
```

**Claude 指令**：
```
「重構 calculateDiscount 使用策略模式取代條件判斷」
```

**之後**：
```javascript
const discountStrategies = {
  regular: (amount) => amount * 0.05,
  premium: (amount) => amount * 0.10,
  vip: (amount) => amount * 0.15 + 10,
  employee: (amount) => amount * 0.25,
  default: () => 0,
};

function calculateDiscount(customer, amount) {
  const strategy = discountStrategies[customer.type] || discountStrategies.default;
  return strategy(amount);
}
```

### 3. 移除重複

**之前**：
```javascript
// 在 UserService 中
async function createUser(data) {
  const user = new User(data);
  user.createdAt = new Date();
  user.updatedAt = new Date();
  user.createdBy = getCurrentUser().id;
  await user.save();
  await sendNotification('user.created', user);
  await logAudit('user.created', user);
  return user;
}

// 在 ProductService 中（重複的邏輯）
async function createProduct(data) {
  const product = new Product(data);
  product.createdAt = new Date();
  product.updatedAt = new Date();
  product.createdBy = getCurrentUser().id;
  await product.save();
  await sendNotification('product.created', product);
  await logAudit('product.created', product);
  return product;
}
```

**Claude 指令**：
```
「找出所有重複的 create/update 模式，提取到基礎服務或 mixin 中」
```

**之後**：
```javascript
// 具有共享邏輯的基礎服務
class BaseService {
  async create(Model, data, eventName) {
    const entity = new Model(data);
    entity.createdAt = new Date();
    entity.updatedAt = new Date();
    entity.createdBy = getCurrentUser().id;
    await entity.save();
    await this.notifyAndLog(eventName, entity);
    return entity;
  }

  async notifyAndLog(event, entity) {
    await Promise.all([
      sendNotification(event, entity),
      logAudit(event, entity)
    ]);
  }
}

// 乾淨的實作
class UserService extends BaseService {
  async createUser(data) {
    return this.create(User, data, 'user.created');
  }
}
```

### 4. 簡化複雜條件判斷

**之前**：
```javascript
function canAccessResource(user, resource) {
  if (user.role === 'admin') {
    return true;
  }
  if (user.role === 'manager' && resource.department === user.department) {
    return true;
  }
  if (user.role === 'employee' && resource.owner === user.id) {
    return true;
  }
  if (resource.isPublic) {
    return true;
  }
  if (resource.sharedWith && resource.sharedWith.includes(user.id)) {
    return true;
  }
  return false;
}
```

**Claude 指令**：
```
「重構 canAccessResource 使用 early returns 和更清晰的邏輯」
```

**之後**：
```javascript
function canAccessResource(user, resource) {
  // 公開資源所有人可存取
  if (resource.isPublic) return true;

  // 檢查明確分享
  if (resource.sharedWith?.includes(user.id)) return true;

  // 基於角色的存取
  return hasRoleBasedAccess(user, resource);
}

function hasRoleBasedAccess(user, resource) {
  const accessRules = {
    admin: () => true,
    manager: () => resource.department === user.department,
    employee: () => resource.owner === user.id,
  };

  return accessRules[user.role]?.() ?? false;
}
```

### 5. 拆分大型檔案

**Claude 指令**：
```
「這個檔案有 800 行。分析並建議如何拆分：
- 將相關函式分組
- 識別不同的職責
- 提出新的檔案結構」
```

**範例回應**：
```
建議拆分 utils.ts（800 行）：

1. utils/string.ts（150 行）
   - formatName, slugify, truncate, capitalize

2. utils/date.ts（120 行）
   - formatDate, parseDate, getRelativeTime

3. utils/validation.ts（200 行）
   - validateEmail, validatePhone, validateUrl

4. utils/api.ts（180 行）
   - fetchWithRetry, handleApiError, buildQueryString

5. utils/dom.ts（150 行）
   - scrollToElement, copyToClipboard, downloadFile

建立 utils/index.ts 重新匯出以保持向後相容性。
```

## 程式碼品質指標

### 讓 Claude 測量

```
「分析這個程式碼庫的程式碼品質指標：
- 平均函式長度
- 圈複雜度
- 重複百分比
- 測試覆蓋率
- 型別覆蓋率」
```

### 設定改善目標

```
「根據指標，建立改善目標：
- 將平均函式長度從 45 行減少到 25 行
- 將圈複雜度從 12 減少到 8
- 將重複從 15% 減少到 5%
- 將測試覆蓋率從 60% 提高到 80%」
```

## 安全重構

### 1. 先有測試

```
「重構前，確保測試覆蓋：
- 為 [函式] 添加涵蓋當前行為的測試
- 執行測試確認通過
- 然後進行重構」
```

### 2. 小步驟、漸進式變更

```
「漸進式重構：
1. 一次提取一個函式
2. 每次提取後執行測試
3. 每次成功變更後提交」
```

### 3. 為高風險變更使用 Feature Flags

```javascript
// 安全推出重構後的程式碼
if (featureFlags.useNewPaymentProcessor) {
  return newPaymentProcessor.process(order);
} else {
  return legacyPaymentProcessor.process(order);
}
```

### 4. 記錄破壞性變更

```
「重構後，記錄：
- 什麼改變了
- 呼叫者的遷移路徑
- 效能影響（如果有的話）」
```

## 重構反模式

### 不要：沒有測試就重構

```
❌ 「重構這段未測試的舊程式碼」

✅ 「首先，為這段舊程式碼添加特徵測試，
    然後在保持測試通過的情況下重構」
```

### 不要：重構時改變行為

```
❌ 「重構這個並同時添加快取」

✅ 「先重構，提交，然後在另一個提交中添加快取」
```

### 不要：一次重構所有東西

```
❌ 「重構整個程式碼庫以使用新模式」

✅ 「先重構使用者模組，驗證可以運作，
    然後再處理其他模組」
```

## Claude 重構指令

### 快速分析
```
「找出最需要重構的前 5 個函式」
```

### 特定改善
```
「重構 [函式] 以減少圈複雜度」
```

### 模式應用
```
「將 repository 模式應用到所有資料庫存取程式碼」
```

### 程式碼異味偵測
```
「識別程式碼異味：過長方法、功能嫉妒、資料泥團」
```

### 前後指標比較
```
「重構後，比較前後的指標：
- 程式碼行數
- 複雜度
- 測試覆蓋率」
```

## 總結

1. **從指標開始** - 了解什麼需要改善
2. **行動前先規劃** - 理解範圍
3. **先測試** - 永遠不重構未測試的程式碼
4. **小步驟** - 一次一個變更
5. **持續驗證** - 每次變更後執行測試
6. **記錄變更** - 幫助未來的開發者
7. **測量改善** - 確認指標改善

**黃金法則**：重構改變結構，不改變行為。如果測試失敗，你破壞了什麼。

---

另見：[功能開發](./feature-development.md) | [Bug 追蹤模式](./bug-hunting.md)
