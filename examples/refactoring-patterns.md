# Refactoring & Code Quality Patterns

> Systematic code improvement with Claude as your refactoring partner.

## Why Refactor with Claude?

Refactoring is:
- **Risky** - Easy to break things
- **Time-consuming** - Many files to touch
- **Tedious** - Repetitive patterns

Claude excels at:
- Identifying refactoring opportunities
- Making consistent changes across files
- Ensuring tests still pass
- Documenting what changed

## The Refactoring Workflow

### Step 1: Identify Opportunities

```
"Analyze this codebase for refactoring opportunities:
- Long functions (>50 lines)
- Duplicated code
- Deep nesting (>3 levels)
- Complex conditionals
- Large files (>500 lines)"
```

Claude returns prioritized list with locations and suggested fixes.

### Step 2: Plan the Refactoring

```
"Create a refactoring plan for [specific issue]:
- What changes are needed
- Which files are affected
- What tests need updating
- Risk assessment"
```

### Step 3: Execute with Tests

```
"Refactor [specific function/module] following the plan.
Ensure all tests pass after each change."
```

### Step 4: Verify and Document

```
"Verify the refactoring is complete:
- All tests pass
- No functionality changed
- Code metrics improved
- Changes documented"
```

## Common Refactoring Patterns

### 1. Extract Function

**Before**:
```javascript
async function processOrder(order) {
  // 50 lines of validation
  if (!order.items) throw new Error('No items');
  if (order.items.length === 0) throw new Error('Empty order');
  for (const item of order.items) {
    if (!item.productId) throw new Error('Missing product ID');
    if (!item.quantity || item.quantity < 1) throw new Error('Invalid quantity');
    const product = await getProduct(item.productId);
    if (!product) throw new Error('Product not found');
    if (product.stock < item.quantity) throw new Error('Insufficient stock');
  }

  // 30 lines of calculation
  let subtotal = 0;
  for (const item of order.items) {
    const product = await getProduct(item.productId);
    subtotal += product.price * item.quantity;
  }
  const tax = subtotal * 0.1;
  const shipping = subtotal > 100 ? 0 : 10;
  const total = subtotal + tax + shipping;

  // 20 lines of saving
  // ...
}
```

**Claude Command**:
```
"Refactor processOrder by extracting:
- validateOrder function
- calculateTotals function
- saveOrder function"
```

**After**:
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

### 2. Replace Conditionals with Polymorphism

**Before**:
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

**Claude Command**:
```
"Refactor calculateDiscount to use a strategy pattern instead of conditionals"
```

**After**:
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

### 3. Remove Duplication

**Before**:
```javascript
// In UserService
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

// In ProductService (duplicated logic)
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

**Claude Command**:
```
"Find all duplicated create/update patterns and extract into a base service or mixin"
```

**After**:
```javascript
// Base service with shared logic
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

// Clean implementations
class UserService extends BaseService {
  async createUser(data) {
    return this.create(User, data, 'user.created');
  }
}
```

### 4. Simplify Complex Conditionals

**Before**:
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

**Claude Command**:
```
"Refactor canAccessResource to use early returns and clearer logic"
```

**After**:
```javascript
function canAccessResource(user, resource) {
  // Public resources accessible to all
  if (resource.isPublic) return true;

  // Check explicit sharing
  if (resource.sharedWith?.includes(user.id)) return true;

  // Role-based access
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

### 5. Break Up Large Files

**Claude Command**:
```
"This file is 800 lines. Analyze and suggest how to split it:
- Group related functions
- Identify distinct responsibilities
- Propose new file structure"
```

**Example Response**:
```
Suggested split for utils.ts (800 lines):

1. utils/string.ts (150 lines)
   - formatName, slugify, truncate, capitalize

2. utils/date.ts (120 lines)
   - formatDate, parseDate, getRelativeTime

3. utils/validation.ts (200 lines)
   - validateEmail, validatePhone, validateUrl

4. utils/api.ts (180 lines)
   - fetchWithRetry, handleApiError, buildQueryString

5. utils/dom.ts (150 lines)
   - scrollToElement, copyToClipboard, downloadFile

Create utils/index.ts to re-export for backwards compatibility.
```

## Code Quality Metrics

### Ask Claude to Measure

```
"Analyze code quality metrics for this codebase:
- Average function length
- Cyclomatic complexity
- Duplication percentage
- Test coverage
- Type coverage"
```

### Set Improvement Targets

```
"Based on metrics, create improvement targets:
- Reduce average function length from 45 to 25 lines
- Reduce cyclomatic complexity from 12 to 8
- Reduce duplication from 15% to 5%
- Increase test coverage from 60% to 80%"
```

## Refactoring Safely

### 1. Always Have Tests First

```
"Before refactoring, ensure test coverage:
- Add tests for [function] covering current behavior
- Run tests to confirm they pass
- Then proceed with refactoring"
```

### 2. Small, Incremental Changes

```
"Refactor incrementally:
1. Extract one function at a time
2. Run tests after each extraction
3. Commit after each successful change"
```

### 3. Use Feature Flags for Risky Changes

```javascript
// Safe rollout of refactored code
if (featureFlags.useNewPaymentProcessor) {
  return newPaymentProcessor.process(order);
} else {
  return legacyPaymentProcessor.process(order);
}
```

### 4. Document Breaking Changes

```
"After refactoring, document:
- What changed
- Migration path for callers
- Performance impact (if any)"
```

## Refactoring Anti-Patterns

### Don't: Refactor Without Tests

```
❌ "Refactor this untested legacy code"

✅ "First, add characterization tests for this legacy code,
    then refactor while keeping tests passing"
```

### Don't: Change Behavior While Refactoring

```
❌ "Refactor this and also add caching"

✅ "Refactor first, commit, then add caching in a separate commit"
```

### Don't: Refactor Everything at Once

```
❌ "Refactor the entire codebase to use the new pattern"

✅ "Refactor the user module first, verify it works,
    then proceed to other modules"
```

## Claude Refactoring Commands

### Quick Analysis
```
"Find the top 5 functions that most need refactoring"
```

### Specific Improvement
```
"Refactor [function] to reduce cyclomatic complexity"
```

### Pattern Application
```
"Apply the repository pattern to all database access code"
```

### Code Smell Detection
```
"Identify code smells: long methods, feature envy, data clumps"
```

### Before/After Metrics
```
"After refactoring, compare metrics with before:
- Lines of code
- Complexity
- Test coverage"
```

## Summary

1. **Start with metrics** - Know what needs improvement
2. **Plan before acting** - Understand the scope
3. **Test first** - Never refactor untested code
4. **Small steps** - One change at a time
5. **Verify continuously** - Run tests after each change
6. **Document changes** - Help future developers
7. **Measure improvement** - Confirm metrics improved

**Golden Rule**: Refactoring changes structure, not behavior. If tests fail, you broke something.

---

See also: [Feature Development](./feature-development.md) | [Bug Hunting Pattern](./bug-hunting.md)
