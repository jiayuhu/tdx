# C# 命名规范详表

## 速查表

| 类别 | 风格 | 正确示例 | 错误示例 |
|------|------|---------|---------|
| 命名空间 | `PascalCase` | `MyApp.Services` | `myApp.services` |
| 类/结构体 | `PascalCase` | `StockManager`, `OrderInfo` | `stockManager`, `order_info` |
| 接口 | `IPascalCase` | `IStockRepository` | `StockRepository`, `IstockRepository` |
| 方法 | `PascalCase` | `GetStocksByDate()` | `getStocksByDate()` |
| 属性 | `PascalCase` | `StockCode`, `RecordDate` | `stockCode`, `record_date` |
| 事件 | `PascalCase` | `StockUpdated`, `OrderPlaced` | `stockUpdated` |
| 委托 | `PascalCase` | `StockChangedHandler` | `stockChangedHandler` |
| 枚举类型 | `PascalCase` | `OrderStatus` | `orderStatus` |
| 枚举值 | `PascalCase` | `OrderStatus.Pending` | `OrderStatus.PENDING` |
| 公有字段 | `PascalCase` | `MaxRetryCount` | `maxRetryCount` |
| 私有字段 | `_camelCase` | `_stockList`, `_logger` | `stockList`, `m_stockList` |
| 参数 | `camelCase` | `stockCode`, `recordDate` | `StockCode`, `stock_code` |
| 局部变量 | `camelCase` | `totalCount`, `isValid` | `TotalCount`, `total_count` |
| 常量 | `PascalCase` | `MaxBatchSize` | `MAX_BATCH_SIZE`, `maxBatchSize` |
| 静态只读 | `PascalCase` | `DefaultTimeout` | `DEFAULT_TIMEOUT` |
| 泛型参数 | `T` 或 `TPascalCase` | `T`, `TKey`, `TValue` | `t`, `key_type` |
| 异步方法 | `PascalCase + Async` | `GetStocksAsync()` | `GetStocks()` (异步方法) |
| 布尔成员 | `Is/Has/Can/Should` | `IsValid`, `HasData` | `Valid`, `DataExists` |

## 详细规则

### 1. 类与接口

```csharp
// 正确：PascalCase 名词/名词短语
public class StockManager { }
public class OrderProcessingService { }
public struct OrderInfo { }

// 接口：I 前缀 + PascalCase
public interface IStockRepository { }
public interface IOrderService { }

// 错误
public class stockManager { }       // camelCase
public class stock_manager { }      // snake_case
public interface StockRepository { } // 缺少 I 前缀
```

### 2. 方法命名

```csharp
// 正确：PascalCase 动词/动词短语
public List<Stock> GetStocksByDate(DateTime date) { }
public async Task<bool> ValidateOrderAsync(Order order) { }
public void ProcessBatch() { }

// 异步方法必须以 Async 结尾
public async Task SaveAsync() { }       // 正确
public async Task Save() { }            // 错误：缺少 Async 后缀

// 返回布尔值的方法
public bool IsValid() { }
public bool HasPermission(string role) { }
public bool CanExecute() { }
```

### 3. 字段与属性

```csharp
public class StockService
{
    // 私有字段：_camelCase
    private readonly ILogger _logger;
    private readonly IStockRepository _repository;
    private int _retryCount;

    // 公有属性：PascalCase
    public string StockCode { get; set; }
    public DateTime RecordDate { get; init; }

    // 常量和静态只读：PascalCase（不用 UPPER_SNAKE）
    public const int MaxBatchSize = 500;
    public static readonly TimeSpan DefaultTimeout = TimeSpan.FromSeconds(30);

    // 错误示例
    private ILogger logger;          // 缺少 _ 前缀
    private ILogger m_logger;        // 匈牙利命名法，已过时
    public const int MAX_BATCH = 500; // C# 不用 UPPER_SNAKE
}
```

### 4. 缩写规则

```csharp
// 两字母缩写：全大写
public class IOHelper { }
public string ID { get; set; }

// 三字母及以上缩写：仅首字母大写
public class HttpClient { }
public string XmlParser { get; set; }
public class ApiController { }

// 错误
public class HTTPClient { }     // 三字母以上不应全大写
public class XmlParser { }       // 正确
public string Id { get; set; }   // 两字母也可以全大写 ID
```

### 5. 枚举

```csharp
// 枚举类型：单数名词 PascalCase
public enum OrderStatus
{
    Pending,
    Processing,
    Completed,
    Cancelled
}

// 标志枚举：复数名词
[Flags]
public enum FilePermissions
{
    None = 0,
    Read = 1,
    Write = 2,
    Execute = 4,
    All = Read | Write | Execute
}

// 错误
public enum OrderStatuses { }    // 非标志枚举不用复数
public enum ORDER_STATUS { }     // 不用 UPPER_SNAKE
```

### 6. 事件与委托

```csharp
// 事件：PascalCase，过去分词或动名词
public event EventHandler<StockEventArgs> StockUpdated;
public event EventHandler<OrderEventArgs> OrderProcessing;

// 委托
public delegate void StockChangedHandler(object sender, StockEventArgs e);

// 事件参数类：以 EventArgs 结尾
public class StockEventArgs : EventArgs
{
    public string StockCode { get; init; }
}
```

### 7. 命名空间

```csharp
// 公司/项目.功能层.子功能
namespace MyCompany.StockTrading.Services { }
namespace MyCompany.StockTrading.Models { }
namespace MyCompany.StockTrading.Data.Repositories { }

// 避免
namespace MyCompany.StockTrading.Services.Helpers.Utils { } // 过深
namespace Utilities { }  // 过于通用
```

### 8. 泛型参数

```csharp
// 单一类型参数用 T
public class Repository<T> where T : class { }

// 多类型参数用描述性名称
public class Dictionary<TKey, TValue> { }
public interface IMapper<TSource, TDestination> { }

// 约束应反映在名称中
public class EntityRepository<TEntity> where TEntity : IEntity { }
```
