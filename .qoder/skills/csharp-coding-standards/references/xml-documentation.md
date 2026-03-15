# C# XML 文档注释模板

## 1. 类文档

```csharp
/// <summary>
/// 股票交易服务，负责处理买入和卖出操作
/// </summary>
/// <remarks>
/// 该服务通过 <see cref="IStockRepository"/> 访问数据，
/// 支持异步批量操作和事务回滚。
/// </remarks>
/// <example>
/// <code>
/// var service = new StockService(repository, logger);
/// await service.ExecuteOrderAsync(order);
/// </code>
/// </example>
public class StockService
{
}
```

## 2. 构造函数

```csharp
/// <summary>
/// 初始化 <see cref="StockService"/> 的新实例
/// </summary>
/// <param name="repository">股票数据仓储</param>
/// <param name="logger">日志记录器</param>
/// <exception cref="ArgumentNullException">
/// <paramref name="repository"/> 或 <paramref name="logger"/> 为 null 时
/// </exception>
public StockService(IStockRepository repository, ILogger<StockService> logger)
{
    _repository = repository ?? throw new ArgumentNullException(nameof(repository));
    _logger = logger ?? throw new ArgumentNullException(nameof(logger));
}
```

## 3. 方法文档

### 完整格式

```csharp
/// <summary>
/// 根据日期查询股票列表
/// </summary>
/// <param name="date">查询日期</param>
/// <param name="cancellationToken">取消令牌</param>
/// <returns>指定日期的股票代码列表；如果无数据，返回空列表</returns>
/// <exception cref="ArgumentOutOfRangeException">
/// <paramref name="date"/> 早于系统最早记录日期时
/// </exception>
/// <exception cref="OperationCanceledException">操作被取消时</exception>
public async Task<List<string>> GetStocksByDateAsync(
    DateTime date,
    CancellationToken cancellationToken = default)
{
}
```

### 简洁格式（简单方法）

```csharp
/// <summary>校验股票代码格式是否合法</summary>
public bool IsValidStockCode(string code)
{
}

/// <summary>获取数据库连接字符串</summary>
public string GetConnectionString() => _connectionString;
```

## 4. 属性文档

```csharp
/// <summary>获取或设置股票代码</summary>
public string StockCode { get; set; }

/// <summary>获取记录创建时间 (UTC)</summary>
public DateTime CreatedAt { get; init; }

/// <summary>
/// 获取或设置最大重试次数
/// </summary>
/// <value>默认值为 3，有效范围 1-10</value>
public int MaxRetryCount { get; set; } = 3;
```

## 5. 枚举文档

```csharp
/// <summary>订单处理状态</summary>
public enum OrderStatus
{
    /// <summary>等待处理</summary>
    Pending,

    /// <summary>正在处理中</summary>
    Processing,

    /// <summary>已完成</summary>
    Completed,

    /// <summary>已取消</summary>
    Cancelled
}
```

## 6. 接口文档

```csharp
/// <summary>
/// 股票数据仓储接口
/// </summary>
/// <remarks>
/// 实现类应确保线程安全。
/// 所有数据库操作方法均为异步。
/// </remarks>
public interface IStockRepository
{
    /// <summary>根据代码查询股票信息</summary>
    /// <param name="code">股票代码 (如 "600001")</param>
    /// <returns>股票信息；未找到时返回 <c>null</c></returns>
    Task<Stock?> FindByCodeAsync(string code);
}
```

## 7. 常用标签参考

| 标签 | 用途 | 示例 |
|------|------|------|
| `<summary>` | 类型/成员摘要 | `/// <summary>获取股票列表</summary>` |
| `<param>` | 参数说明 | `/// <param name="code">股票代码</param>` |
| `<returns>` | 返回值说明 | `/// <returns>股票列表</returns>` |
| `<exception>` | 可能抛出的异常 | `/// <exception cref="ArgumentNullException">` |
| `<remarks>` | 补充说明 | `/// <remarks>该方法是线程安全的</remarks>` |
| `<example>` | 使用示例 | 包含 `<code>` 代码块 |
| `<see cref=""/>` | 行内引用 | `/// 参见 <see cref="StockService"/>` |
| `<seealso cref=""/>` | 相关引用 | `/// <seealso cref="IStockRepository"/>` |
| `<c>` | 行内代码 | `/// 返回 <c>null</c>` |
| `<value>` | 属性值说明 | `/// <value>默认值为 3</value>` |
| `<inheritdoc/>` | 继承基类/接口文档 | `/// <inheritdoc/>` |
| `<typeparam>` | 泛型参数 | `/// <typeparam name="T">实体类型</typeparam>` |
| `<paramref>` | 引用参数名 | `/// 当 <paramref name="code"/> 为空时` |

## 8. 文档规则

- 所有 `public` / `protected` 成员必须有 XML 文档
- `private` / `internal` 成员建议有，但不强制
- 摘要使用完整句子，以句号结尾（中文可省略）
- `<returns>` 说明返回 `null` 的条件
- `<exception>` 列出所有可能直接抛出的异常
- 使用 `<inheritdoc/>` 避免接口实现类重复文档
- 启用 `<GenerateDocumentationFile>true</GenerateDocumentationFile>` 生成 XML 文件
