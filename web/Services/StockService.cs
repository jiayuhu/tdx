using Microsoft.EntityFrameworkCore;
using web.Data;

namespace web.Services;

/// <summary>
/// 股票数据服务（EF Core 版本）
/// </summary>
public class StockService
{
    private readonly IDbContextFactory<TdxDbContext> _contextFactory;
    private readonly ILogger<StockService> _logger;

    public StockService(IDbContextFactory<TdxDbContext> contextFactory, ILogger<StockService> logger)
    {
        _contextFactory = contextFactory;
        _logger = logger;
    }

    /// <summary>
    /// 获取 B01 数据
    /// </summary>
    public async Task<List<B01Stock>> GetB01DataAsync()
    {
        try
        {
            await using var context = await _contextFactory.CreateDbContextAsync();
            return await context.B01
                .OrderByDescending(s => s.RecordDate)
                .ThenByDescending(s => s.Id)
                .Take(1000)
                .ToListAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "查询 B01 失败");
            return new List<B01Stock>();
        }
    }

    /// <summary>
    /// 获取 B01_DELTA 数据
    /// </summary>
    public async Task<List<B01DeltaStock>> GetB01DeltaDataAsync()
    {
        try
        {
            await using var context = await _contextFactory.CreateDbContextAsync();
            return await context.B01Delta
                .OrderByDescending(s => s.EntryDate)
                .ThenByDescending(s => s.Id)
                .Take(1000)
                .ToListAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "查询 B01_DELTA 失败");
            return new List<B01DeltaStock>();
        }
    }

    /// <summary>
    /// 获取 B02 数据
    /// </summary>
    public async Task<List<B02Stock>> GetB02DataAsync()
    {
        try
        {
            await using var context = await _contextFactory.CreateDbContextAsync();
            return await context.B02
                .OrderByDescending(s => s.RecordDate)
                .ThenByDescending(s => s.Id)
                .Take(1000)
                .ToListAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "查询 B02 失败");
            return new List<B02Stock>();
        }
    }

    /// <summary>
    /// 获取 B02_DELTA 数据
    /// </summary>
    public async Task<List<B02DeltaStock>> GetB02DeltaDataAsync()
    {
        try
        {
            await using var context = await _contextFactory.CreateDbContextAsync();
            return await context.B02Delta
                .OrderByDescending(s => s.EntryDate)
                .ThenByDescending(s => s.Id)
                .Take(1000)
                .ToListAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "查询 B02_DELTA 失败");
            return new List<B02DeltaStock>();
        }
    }

    /// <summary>
    /// 获取 BA1 数据
    /// </summary>
    public async Task<List<BA1Stock>> GetBA1DataAsync()
    {
        Console.WriteLine("=== 开始查询 BA1 ===");
        try
        {
            await using var context = await _contextFactory.CreateDbContextAsync();
            Console.WriteLine($"数据库连接成功");
            
            var query = context.BA1
                .OrderByDescending(s => s.RecordDate)
                .ThenByDescending(s => s.Id)
                .Take(1000);
            
            Console.WriteLine($"SQL: {query.ToQueryString()}");
            
            var result = await query.ToListAsync();
            Console.WriteLine($"BA1 查询到 {result.Count} 条数据");
            
            return result;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"BA1 查询失败：{ex.Message}");
            Console.WriteLine($"堆栈：{ex.StackTrace}");
            return new List<BA1Stock>();
        }
    }

    /// <summary>
    /// 获取 BA1_DELTA 数据
    /// </summary>
    public async Task<List<BA1DeltaStock>> GetBA1DeltaDataAsync()
    {
        Console.WriteLine("=== 开始查询 BA1_DELTA ===");
        try
        {
            await using var context = await _contextFactory.CreateDbContextAsync();
            Console.WriteLine("数据库连接成功");
            
            var query = context.BA1Delta
                .OrderByDescending(s => s.EntryDate)
                .ThenByDescending(s => s.Id)
                .Take(1000);
            
            Console.WriteLine($"SQL: {query.ToQueryString()}");
            
            var result = await query.ToListAsync();
            Console.WriteLine($"查询到 {result.Count} 条数据");
            
            return result;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"查询 BA1_DELTA 失败：{ex.Message}");
            Console.WriteLine($"堆栈：{ex.StackTrace}");
            return new List<BA1DeltaStock>();
        }
    }

    /// <summary>
    /// 获取 BA2 数据
    /// </summary>
    public async Task<List<BA2Stock>> GetBA2DataAsync()
    {
        try
        {
            await using var context = await _contextFactory.CreateDbContextAsync();
            return await context.BA2
                .OrderByDescending(s => s.RecordDate)
                .ThenByDescending(s => s.Id)
                .Take(1000)
                .ToListAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "查询 BA2 失败");
            return new List<BA2Stock>();
        }
    }

    /// <summary>
    /// 获取 BA2_DELTA 数据
    /// </summary>
    public async Task<List<BA2DeltaStock>> GetBA2DeltaDataAsync()
    {
        Console.WriteLine("=== 开始查询 BA2_DELTA ===");
        try
        {
            await using var context = await _contextFactory.CreateDbContextAsync();
            Console.WriteLine("数据库连接成功");
            
            var query = context.BA2Delta
                .OrderByDescending(s => s.EntryDate)
                .ThenByDescending(s => s.Id)
                .Take(1000);
            
            Console.WriteLine($"SQL: {query.ToQueryString()}");
            
            var result = await query.ToListAsync();
            Console.WriteLine($"查询到 {result.Count} 条数据");
            
            return result;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"查询 BA2_DELTA 失败：{ex.Message}");
            Console.WriteLine($"堆栈：{ex.StackTrace}");
            return new List<BA2DeltaStock>();
        }
    }
}
