using Microsoft.EntityFrameworkCore;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace web.Data;

/// <summary>
/// 日报实体基类（5 列：id, stock_code, stock_name, record_date, created_at）
/// </summary>
public abstract class StockBase
{
    [Key]
    [Column("id")]
    public int Id { get; set; }

    [Column("stock_code")]
    public string StockCode { get; set; } = string.Empty;

    [Column("stock_name")]
    public string StockName { get; set; } = string.Empty;

    [Column("record_date")]
    public DateTime RecordDate { get; set; }            // UTC 时间

    [Column("created_at")]
    public DateTime CreatedAt { get; set; }             // UTC 时间

    /// <summary>
    /// 获取东八区格式的记录日期（仅日期）
    /// </summary>
    [NotMapped]
    public string RecordDateCst => RecordDate.AddHours(8).ToString("yyyy-MM-dd");
}

/// <summary>
/// 增量实体基类（7 列：继承 StockBase 5 列 + entry_date, buy_point）
/// </summary>
public abstract class DeltaStockBase : StockBase
{
    [Column("entry_date")]
    public DateTime? EntryDate { get; set; }            // UTC 时间

    [Column("buy_point")]
    public decimal? BuyPoint { get; set; }

    /// <summary>
    /// 获取东八区格式的入选日期（仅日期）
    /// </summary>
    [NotMapped]
    public string EntryDateCst => EntryDate?.AddHours(8).ToString("yyyy-MM-dd") ?? "";
}

// ── 长线选股 ──

/// <summary>B01 长线日报 - 优质小盘股 - 低档金叉</summary>
[Table("b01")]
public class B01Stock : StockBase { }

/// <summary>B01_DELTA 长线新增</summary>
[Table("b01_delta")]
public class B01DeltaStock : DeltaStockBase { }

/// <summary>B02 长线日报 - 优质小盘股 - 高档金叉</summary>
[Table("b02")]
public class B02Stock : StockBase { }

/// <summary>B02_DELTA 长线新增</summary>
[Table("b02_delta")]
public class B02DeltaStock : DeltaStockBase { }

// ── 短线选股 ──

/// <summary>BA1 短线日报 - AAA 选股池 - 低档金叉</summary>
[Table("ba1")]
public class BA1Stock : StockBase { }

/// <summary>BA1_DELTA 短线新增</summary>
[Table("ba1_delta")]
public class BA1DeltaStock : DeltaStockBase { }

/// <summary>BA2 短线日报 - AAA 选股池 - 高档金叉</summary>
[Table("ba2")]
public class BA2Stock : StockBase { }

/// <summary>BA2_DELTA 短线新增</summary>
[Table("ba2_delta")]
public class BA2DeltaStock : DeltaStockBase { }

/// <summary>
/// 数据库上下文
/// </summary>
public class TdxDbContext : DbContext
{
    public TdxDbContext(DbContextOptions<TdxDbContext> options)
        : base(options)
    {
    }

    public DbSet<B01Stock> B01 { get; set; } = null!;
    public DbSet<B01DeltaStock> B01Delta { get; set; } = null!;
    public DbSet<B02Stock> B02 { get; set; } = null!;
    public DbSet<B02DeltaStock> B02Delta { get; set; } = null!;
    public DbSet<BA1Stock> BA1 { get; set; } = null!;
    public DbSet<BA1DeltaStock> BA1Delta { get; set; } = null!;
    public DbSet<BA2Stock> BA2 { get; set; } = null!;
    public DbSet<BA2DeltaStock> BA2Delta { get; set; } = null!;

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        // TPC：每个具体实体类映射到独立表，基类不建表
        modelBuilder.Entity<StockBase>().UseTpcMappingStrategy();
    }
}
