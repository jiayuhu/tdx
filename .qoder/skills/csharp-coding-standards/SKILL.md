---
name: csharp-coding-standards
description: 'Use when: 编写、审查或重构 C# 代码时。确保遵循 .NET 官方编码规范和最佳实践。适用于代码生成、代码审查、Bug 修复、重构等所有 C# 开发场景。关键词: C#, CSharp, .NET, 编码规范, 代码风格, 命名规范, XML文档, async, LINQ, 依赖注入'
---

# C# 编码规范

本规范适用于所有 C# 项目的代码编写、审查和重构。基于 .NET 官方 Framework Design Guidelines 及社区最佳实践。

---

## 1. 命名规范

| 类别 | 风格 | 示例 |
|------|------|------|
| 类/结构体/枚举 | `PascalCase` | `StockManager`, `OrderInfo` |
| 接口 | `IPascalCase` | `IStockRepository` |
| 方法/属性/事件 | `PascalCase` | `GetStocksAsync()`, `StockCode` |
| 参数/局部变量 | `camelCase` | `stockCode`, `recordDate` |
| 私有字段 | `_camelCase` | `_logger`, `_repository` |
| 常量/静态只读 | `PascalCase` | `MaxBatchSize`, `DefaultTimeout` |
| 泛型参数 | `T` / `TPascalCase` | `T`, `TKey`, `TValue` |
| 命名空间 | `PascalCase` | `MyApp.Services.Stock` |
| 异步方法 | `PascalCase + Async` | `SaveAsync()`, `GetDataAsync()` |
| 布尔成员 | `Is/Has/Can/Should` | `IsValid`, `HasPermission` |

**核心原则**：
- 两字母缩写全大写：`IO`, `ID`
- 三字母以上缩写仅首字母大写：`Http`, `Xml`, `Api`
- 不使用匈牙利命名法（`m_`, `str`, `int` 前缀）
- 不使用 `UPPER_SNAKE_CASE`（与 Java/Python 不同）
- 枚举类型用单数，`[Flags]` 枚举用复数

详细命名对照表见 [naming-conventions.md](./references/naming-conventions.md)

---

## 2. 代码格式化

### 花括号与缩进
```csharp
// Allman 风格：花括号独占一行
public class StockService
{
    public void Process()
    {
        if (condition)
        {
            Execute();
        }
    }
}
```
- 缩进：4 个空格
- 行宽：最大 120 字符
- 单行属性/方法可用表达式体：`public string Name => _name;`

### 访问修饰符
```csharp
// 始终显式声明访问修饰符
public class StockService          // 不省略
{
    private readonly ILogger _logger;  // 不省略 private
    internal void Helper() { }         // 不省略 internal
}
```

### using 指令
```csharp
// 按 System → 第三方 → 项目命名空间排序
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

using Microsoft.Extensions.Logging;
using Newtonsoft.Json;

using MyApp.Models;
using MyApp.Services;
```

### var 关键字
```csharp
// 右侧类型明显时用 var
var stocks = new List<string>();
var logger = LoggerFactory.CreateLogger<StockService>();

// 类型不明显时显式声明
int retryCount = GetRetryCount();
StockInfo stock = MapToInfo(data);
```

### 成员排列顺序
```
1. 常量 (const)
2. 静态字段
3. 实例字段
4. 构造函数
5. 属性
6. 公有方法
7. 私有方法
```

---

## 3. XML 文档注释

### 基本规则
- 所有 `public` / `protected` 成员必须有 XML 文档
- `private` / `internal` 建议有，但不强制

### 常用格式
```csharp
/// <summary>
/// 根据日期查询股票列表
/// </summary>
/// <param name="date">查询日期</param>
/// <param name="cancellationToken">取消令牌</param>
/// <returns>股票代码列表；无数据时返回空列表</returns>
/// <exception cref="ArgumentOutOfRangeException">日期超出范围时</exception>
public async Task<List<string>> GetStocksByDateAsync(
    DateTime date,
    CancellationToken cancellationToken = default)
```

### 简洁格式
```csharp
/// <summary>校验股票代码格式</summary>
public bool IsValidCode(string code) => CodeRegex.IsMatch(code);
```

**核心标签**：`<summary>`, `<param>`, `<returns>`, `<exception>`, `<remarks>`, `<example>`, `<see cref=""/>`

接口实现用 `/// <inheritdoc/>` 继承文档，避免重复。

完整模板见 [xml-documentation.md](./references/xml-documentation.md)

---

## 4. LINQ 最佳实践

### 方法语法 vs 查询语法
```csharp
// 简单过滤/投影：方法语法
var active = stocks.Where(s => s.IsActive).Select(s => s.Code);

// 多 join/let 复杂查询：查询语法
var result = from s in stocks
             join p in prices on s.Code equals p.Code
             where s.IsActive
             select new { s.Name, p.Price };
```

### 延迟执行
```csharp
// IEnumerable 是延迟执行的 — 每次遍历都会重新计算
var filtered = stocks.Where(s => s.IsActive);  // 此时未执行

// 需要多次遍历时，先物化
var list = stocks.Where(s => s.IsActive).ToList();
Console.WriteLine($"数量：{list.Count}");
foreach (var s in list) { ... }
```

### 链式调用格式
```csharp
// 每个操作独占一行
var result = stocks
    .Where(s => s.IsActive)
    .OrderByDescending(s => s.UpdatedAt)
    .Select(s => new StockDto(s.Code, s.Name))
    .ToList();
```

**避免**：
- 在 LINQ 中产生副作用（如修改外部变量）
- 过度嵌套 LINQ 导致可读性差
- 忘记 `ToList()` 导致多次枚举

---

## 5. async/await 模式

| 规则 | 说明 |
|------|------|
| async 一路到底 | 避免 `.Result` 和 `.Wait()` 同步阻塞 |
| 返回 Task | 禁止 `async void`（事件处理器除外） |
| Async 后缀 | 异步方法名以 `Async` 结尾 |
| ConfigureAwait | 库代码加 `.ConfigureAwait(false)` |
| CancellationToken | 长时间操作接受 `CancellationToken` 参数 |
| 并行执行 | 用 `Task.WhenAll` 而非顺序 await |

```csharp
// 标准异步方法签名
public async Task<List<Stock>> GetStocksAsync(
    CancellationToken cancellationToken = default)
{
    var data = await _repository
        .QueryAsync(cancellationToken)
        .ConfigureAwait(false);
    return data;
}
```

**ValueTask vs Task**：频繁同步返回缓存结果的方法用 `ValueTask`，一般情况用 `Task`。

详细模式和死锁场景见 [async-patterns.md](./references/async-patterns.md)

---

## 6. 异常处理

### 捕获具体异常
```csharp
try
{
    await ProcessAsync();
}
catch (OperationCanceledException)
{
    _logger.LogWarning("操作被取消");
}
catch (InvalidOperationException ex)
{
    _logger.LogError(ex, "操作无效");
    throw;  // 用 throw; 而非 throw ex; 保留堆栈
}
```

### Guard 子句
```csharp
public void Process(string code, ILogger logger)
{
    ArgumentNullException.ThrowIfNull(logger);  // .NET 6+
    ArgumentException.ThrowIfNullOrEmpty(code);  // .NET 7+

    // 主逻辑
}
```

### 异常过滤器
```csharp
catch (HttpRequestException ex) when (ex.StatusCode == HttpStatusCode.NotFound)
{
    return null;
}
```

### 自定义异常
```csharp
public class StockNotFoundException : Exception
{
    public string StockCode { get; }

    public StockNotFoundException(string stockCode)
        : base($"股票 {stockCode} 未找到")
    {
        StockCode = stockCode;
    }

    public StockNotFoundException(string stockCode, Exception innerException)
        : base($"股票 {stockCode} 未找到", innerException)
    {
        StockCode = stockCode;
    }
}
```

**规则**：
- 按从具体到一般的顺序排列 catch 块
- 不要用异常控制正常流程
- 最顶层（入口/中间件）可以捕获 `Exception` 做全局处理

---

## 7. Null 安全

### 启用可空引用类型
```xml
<!-- .csproj -->
<PropertyGroup>
    <Nullable>enable</Nullable>
</PropertyGroup>
```

### null 检查模式
```csharp
// 模式匹配（推荐）
if (stock is null) return;
if (stock is not null) Process(stock);

// null 条件运算符
var name = stock?.Name;
var first = stocks?.FirstOrDefault();

// null 合并
string name = stock?.Name ?? "未知";
_cache ??= new Dictionary<string, Stock>();

// 避免
if (stock == null)   // 可被运算符重载影响
string name = stock!.Name;  // 除非确定非 null，否则不用 !
```

### 返回值
```csharp
// 返回空集合而非 null
public List<Stock> GetStocks()
{
    if (!HasData) return [];  // C# 12 集合表达式
    return _stocks;
}

// 可能返回 null 时用 ? 标注
public Stock? FindByCode(string code) => _stocks.FirstOrDefault(s => s.Code == code);
```

---

## 8. 项目结构

### 解决方案组织
```
Solution/
├── src/
│   ├── MyApp.Api/           # Web API 层
│   ├── MyApp.Core/          # 业务逻辑和领域模型
│   ├── MyApp.Infrastructure/ # 数据访问、外部服务
│   └── MyApp.Shared/        # 共享 DTO、工具类
├── tests/
│   ├── MyApp.Core.Tests/
│   └── MyApp.Api.Tests/
└── MyApp.sln
```

**规则**：
- 命名空间与文件夹结构匹配
- 每个文件包含一个主类型，文件名 = 类名
- 接口和实现分离（`IStockRepository` 在 Core，`StockRepository` 在 Infrastructure）
- 配置使用 `appsettings.json` + Options 模式

---

## 9. 依赖注入

### 构造函数注入（首选）
```csharp
public class StockService
{
    private readonly IStockRepository _repository;
    private readonly ILogger<StockService> _logger;

    public StockService(IStockRepository repository, ILogger<StockService> logger)
    {
        _repository = repository;
        _logger = logger;
    }
}
```

### 生命周期选择

| 生命周期 | 场景 | 示例 |
|---------|------|------|
| Transient | 轻量无状态服务 | Validator, Mapper |
| Scoped | 请求级别状态 | DbContext, UnitOfWork |
| Singleton | 全局共享状态 | Cache, Configuration |

### 注册封装
```csharp
// 用扩展方法封装注册逻辑
public static class ServiceCollectionExtensions
{
    public static IServiceCollection AddStockServices(this IServiceCollection services)
    {
        services.AddScoped<IStockRepository, StockRepository>();
        services.AddTransient<IStockService, StockService>();
        return services;
    }
}
```

**避免**：
- Service Locator 模式（`services.GetService<T>()`）
- 构造函数参数超过 5 个（考虑拆分职责）
- Singleton 中注入 Scoped 服务（Captive Dependency）

---

## 10. 常见反模式

| 反模式 | 正确做法 |
|--------|---------|
| `async void` | 返回 `Task`（事件处理器除外） |
| `.Result` / `.Wait()` | `await` 异步等待 |
| `throw ex;` | `throw;` 保留堆栈 |
| 空 catch 块 | 至少记录日志 |
| 忘记 Dispose | `using` / `await using` 语句 |
| 循环字符串 `+=` | `StringBuilder` 或 `string.Join` |
| 过度使用 `dynamic` | 具体类型或泛型 |
| God Class | 按职责拆分为多个类 |
| 全局 static 可变状态 | 依赖注入 |
| `stock!.Name` 强制忽略 null | 正确处理 null 分支 |
| `GC.Collect()` 手动 GC | 正确实现 IDisposable |
| `new` 隐藏基类成员 | `override` 重写 |

详细说明及代码对比见 [anti-patterns.md](./references/anti-patterns.md)
