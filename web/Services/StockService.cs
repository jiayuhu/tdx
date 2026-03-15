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
    /// 通用日报查询（按 record_date 倒序）
    /// </summary>
    private async Task<List<T>> QueryStocksAsync<T>(
        Func<TdxDbContext, DbSet<T>> dbSetSelector,
        string tableName,
        int limit = 1000) where T : StockBase
    {
        try
        {
            await using var context = await _contextFactory.CreateDbContextAsync();
            return await dbSetSelector(context)
                .OrderByDescending(s => s.RecordDate)
                .ThenByDescending(s => s.Id)
                .Take(limit)
                .ToListAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "查询 {TableName} 失败", tableName);
            return [];
        }
    }

    /// <summary>
    /// 通用增量查询（按 entry_date 倒序）
    /// </summary>
    private async Task<List<T>> QueryDeltaAsync<T>(
        Func<TdxDbContext, DbSet<T>> dbSetSelector,
        string tableName,
        int limit = 1000) where T : DeltaStockBase
    {
        try
        {
            await using var context = await _contextFactory.CreateDbContextAsync();
            return await dbSetSelector(context)
                .OrderByDescending(s => s.EntryDate)
                .ThenByDescending(s => s.Id)
                .Take(limit)
                .ToListAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "查询 {TableName} 失败", tableName);
            return [];
        }
    }

    // ── 长线选股 ──

    public Task<List<B01Stock>> GetB01DataAsync()
        => QueryStocksAsync(c => c.B01, "B01");

    public Task<List<B01DeltaStock>> GetB01DeltaDataAsync()
        => QueryDeltaAsync(c => c.B01Delta, "B01_DELTA");

    public Task<List<B02Stock>> GetB02DataAsync()
        => QueryStocksAsync(c => c.B02, "B02");

    public Task<List<B02DeltaStock>> GetB02DeltaDataAsync()
        => QueryDeltaAsync(c => c.B02Delta, "B02_DELTA");

    // ── 短线选股 ──

    public Task<List<BA1Stock>> GetBA1DataAsync()
        => QueryStocksAsync(c => c.BA1, "BA1");

    public Task<List<BA1DeltaStock>> GetBA1DeltaDataAsync()
        => QueryDeltaAsync(c => c.BA1Delta, "BA1_DELTA");

    public Task<List<BA2Stock>> GetBA2DataAsync()
        => QueryStocksAsync(c => c.BA2, "BA2");

    public Task<List<BA2DeltaStock>> GetBA2DeltaDataAsync()
        => QueryDeltaAsync(c => c.BA2Delta, "BA2_DELTA");
}
