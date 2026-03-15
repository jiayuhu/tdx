# C# async/await 模式

## 1. async 一路到底

```csharp
// 正确：整个调用链都用 async/await
public async Task<List<Stock>> GetStocksAsync()
{
    var data = await _repository.QueryAsync();
    return await ProcessDataAsync(data);
}

// 错误：在 async 链中同步阻塞 — 可能导致死锁
public List<Stock> GetStocks()
{
    // 死锁风险！
    var data = _repository.QueryAsync().Result;
    return ProcessDataAsync(data).GetAwaiter().GetResult();
}
```

**核心原则**：一旦引入 async，调用链上的所有方法都应该是 async。

## 2. 避免 async void

```csharp
// 错误：async void 无法被 await，异常无法捕获
async void ProcessStock(string code)
{
    await _service.UpdateAsync(code); // 异常会直接崩溃进程
}

// 正确：返回 Task
async Task ProcessStockAsync(string code)
{
    await _service.UpdateAsync(code);
}

// 唯一例外：事件处理器
async void OnButtonClick(object sender, EventArgs e)
{
    try
    {
        await ProcessAsync();
    }
    catch (Exception ex)
    {
        _logger.LogError(ex, "处理失败");
    }
}
```

## 3. ConfigureAwait

```csharp
// 库代码：使用 ConfigureAwait(false) 避免死锁
public async Task<string> ReadDataAsync()
{
    var content = await File.ReadAllTextAsync(path)
        .ConfigureAwait(false);
    return Parse(content);
}

// UI / ASP.NET Controller：不加 ConfigureAwait（需要同步上下文）
public async Task<IActionResult> GetStocks()
{
    var stocks = await _service.GetStocksAsync();
    return Ok(stocks);
}
```

**规则**：
- 类库项目：所有 await 加 `.ConfigureAwait(false)`
- 应用层（Controller、UI）：不加

## 4. CancellationToken

```csharp
// 所有长时间操作接受 CancellationToken
public async Task<List<Stock>> SearchAsync(
    string query,
    CancellationToken cancellationToken = default)
{
    // 传递给下游调用
    var results = await _repository
        .QueryAsync(query, cancellationToken)
        .ConfigureAwait(false);

    // 在循环中检查取消
    foreach (var item in results)
    {
        cancellationToken.ThrowIfCancellationRequested();
        await ProcessItemAsync(item, cancellationToken)
            .ConfigureAwait(false);
    }

    return results;
}

// 调用方使用
using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(30));
try
{
    var stocks = await service.SearchAsync("query", cts.Token);
}
catch (OperationCanceledException)
{
    _logger.LogWarning("操作超时或被取消");
}
```

## 5. 并行执行

```csharp
// 并行执行多个独立任务
public async Task UpdateAllAsync(List<string> codes)
{
    var tasks = codes.Select(code => UpdateStockAsync(code));
    await Task.WhenAll(tasks).ConfigureAwait(false);
}

// 控制并行度
public async Task UpdateAllAsync(List<string> codes, int maxParallel = 5)
{
    using var semaphore = new SemaphoreSlim(maxParallel);

    var tasks = codes.Select(async code =>
    {
        await semaphore.WaitAsync().ConfigureAwait(false);
        try
        {
            await UpdateStockAsync(code).ConfigureAwait(false);
        }
        finally
        {
            semaphore.Release();
        }
    });

    await Task.WhenAll(tasks).ConfigureAwait(false);
}

// 任一完成
var firstResult = await Task.WhenAny(task1, task2, task3);
```

## 6. ValueTask vs Task

```csharp
// 频繁返回缓存结果的场景用 ValueTask 减少分配
public ValueTask<Stock?> GetCachedStockAsync(string code)
{
    if (_cache.TryGetValue(code, out var stock))
    {
        return ValueTask.FromResult<Stock?>(stock); // 无堆分配
    }
    return new ValueTask<Stock?>(LoadFromDbAsync(code));
}

// 一般情况用 Task 即可
public Task<List<Stock>> GetAllStocksAsync() { }
```

**ValueTask 使用规则**：
- 方法高频调用且经常同步完成时使用
- 不能 await 多次
- 不能并行 await
- 不确定时用 `Task`

## 7. 异步释放

```csharp
// IAsyncDisposable 模式
public class StockService : IAsyncDisposable
{
    private readonly DbConnection _connection;

    public async ValueTask DisposeAsync()
    {
        if (_connection is not null)
        {
            await _connection.DisposeAsync().ConfigureAwait(false);
        }
    }
}

// 使用 await using
await using var service = new StockService();
await service.ProcessAsync();
// 自动调用 DisposeAsync
```

## 8. 异步流

```csharp
// IAsyncEnumerable 处理大量数据
public async IAsyncEnumerable<Stock> StreamStocksAsync(
    [EnumeratorCancellation] CancellationToken ct = default)
{
    await foreach (var batch in _repository.GetBatchesAsync(ct))
    {
        foreach (var stock in batch)
        {
            yield return stock;
        }
    }
}

// 消费异步流
await foreach (var stock in service.StreamStocksAsync(cancellationToken))
{
    ProcessStock(stock);
}
```

## 9. 常见死锁场景

```csharp
// 场景 1：UI 线程同步等待异步结果
// MainWindow.xaml.cs
void OnLoad()
{
    // 死锁！UI 线程被阻塞，await 的 continuation 也需要 UI 线程
    var data = GetDataAsync().Result;
}

// 修复：async 一路到底
async void OnLoad()
{
    var data = await GetDataAsync();
}

// 场景 2：ASP.NET 中 .Result 阻塞
// 修复：所有 Controller 方法改为 async Task<IActionResult>

// 场景 3：库代码未加 ConfigureAwait(false)
// 修复：库方法所有 await 加 .ConfigureAwait(false)
```
