# C# 常见反模式

## 1. async void

```csharp
// 错误：异常无法被调用方捕获，会导致进程崩溃
async void SaveData()
{
    await _repository.SaveAsync();
}

// 正确：返回 Task
async Task SaveDataAsync()
{
    await _repository.SaveAsync();
}
```

**唯一例外**：事件处理器（如 `async void OnClick`），且必须内部 try-catch。

## 2. .Result / .Wait() 同步阻塞

```csharp
// 错误：可能导致死锁
var data = GetDataAsync().Result;
GetDataAsync().Wait();

// 正确：await
var data = await GetDataAsync();

// 如果确实在同步上下文中需要调用异步方法（极少数情况）
var data = Task.Run(() => GetDataAsync()).GetAwaiter().GetResult();
```

## 3. 空 catch 块

```csharp
// 错误：异常被静默吞掉
try
{
    Process();
}
catch (Exception)
{
}

// 正确：至少记录日志
try
{
    Process();
}
catch (Exception ex)
{
    _logger.LogError(ex, "处理失败");
}

// 如果确实可以忽略，用注释说明原因
try
{
    CleanupTempFiles();
}
catch (IOException)
{
    // 临时文件清理失败不影响主流程
}
```

## 4. throw ex 丢失堆栈

```csharp
// 错误：throw ex 重置堆栈跟踪
try
{
    Process();
}
catch (Exception ex)
{
    _logger.LogError(ex, "错误");
    throw ex;  // 堆栈信息丢失！
}

// 正确：throw 保留原始堆栈
catch (Exception ex)
{
    _logger.LogError(ex, "错误");
    throw;     // 保留完整堆栈
}

// 或包装为新异常
catch (Exception ex)
{
    throw new ServiceException("处理失败", ex);  // ex 作为内部异常
}
```

## 5. 忘记 Dispose

```csharp
// 错误：资源泄漏
var connection = new SqlConnection(connectionString);
await connection.OpenAsync();
var result = await connection.QueryAsync(sql);
// connection 从未关闭！

// 正确：using 语句
await using var connection = new SqlConnection(connectionString);
await connection.OpenAsync();
var result = await connection.QueryAsync(sql);
// 自动 Dispose

// using 声明（C# 8+）
using var reader = new StreamReader(path);
var content = await reader.ReadToEndAsync();
```

## 6. 字符串拼接性能

```csharp
// 错误：循环中 += 每次创建新字符串
string result = "";
foreach (var item in items)
{
    result += item.ToString() + ", ";
}

// 正确：StringBuilder
var sb = new StringBuilder();
foreach (var item in items)
{
    sb.Append(item).Append(", ");
}
var result = sb.ToString();

// 更佳：string.Join
var result = string.Join(", ", items);

// 少量拼接用插值
var message = $"共 {count} 条记录，耗时 {elapsed}ms";
```

## 7. 过度使用 dynamic

```csharp
// 错误：失去编译时类型检查
dynamic data = GetData();
var name = data.Name;  // 运行时才能发现错误

// 正确：使用具体类型或泛型
StockInfo data = GetData();
var name = data.Name;  // 编译时检查
```

## 8. God Class（上帝类）

```csharp
// 错误：一个类承担过多职责
public class StockManager
{
    public void FetchFromApi() { }
    public void SaveToDatabase() { }
    public void SendEmail() { }
    public void GenerateReport() { }
    public void ValidateInput() { }
}

// 正确：按职责拆分
public class StockFetcher { }       // 数据获取
public class StockRepository { }    // 数据持久化
public class NotificationService { } // 通知
public class ReportGenerator { }    // 报告生成
```

## 9. 滥用 static

```csharp
// 错误：全局可变状态，难以测试
public static class AppState
{
    public static DbConnection Connection { get; set; }
    public static UserInfo CurrentUser { get; set; }
}

// 正确：通过依赖注入
public class AppContext
{
    private readonly IDbConnectionFactory _connectionFactory;

    public AppContext(IDbConnectionFactory factory)
    {
        _connectionFactory = factory;
    }
}
```

**static 的合理用途**：纯函数工具方法、扩展方法、常量。

## 10. 忽略 nullable 警告

```csharp
// 错误：用 ! 强制忽略 nullable 警告
string name = GetName()!;  // 如果返回 null 则运行时 NRE

// 正确：正确处理 null
string? name = GetName();
if (name is not null)
{
    Process(name);
}

// 或使用 null 合并
string name = GetName() ?? "默认值";
```

## 11. 手动调用 GC

```csharp
// 错误：几乎不应该手动调用
GC.Collect();
GC.WaitForPendingFinalizers();

// 正确：让 GC 自动管理
// 确保实现 IDisposable/IAsyncDisposable 释放非托管资源即可
```

## 12. new 隐藏基类成员

```csharp
// 错误：new 隐藏基类方法，可能导致多态行为不一致
public class DerivedService : BaseService
{
    public new void Process() { }  // 隐藏而非重写
}

// 正确：使用 override
public class DerivedService : BaseService
{
    public override void Process() { }  // 多态正确
}
```
