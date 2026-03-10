using Microsoft.EntityFrameworkCore;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace web.Data;

/// <summary>
/// B01 长线日报实体（5 列）
/// </summary>
[Table("b01")]
public class B01Stock
{
    [Key]
    [Column("id")]
    public int Id { get; set; }                    // 第 1 列

    [Column("stock_code")]
    public string StockCode { get; set; } = string.Empty;  // 第 2 列

    [Column("stock_name")]
    public string StockName { get; set; } = string.Empty;  // 第 3 列

    [Column("record_date")]
    public DateTime RecordDate { get; set; }       // 第 4 列（UTC 时间）

    [Column("created_at")]
    public DateTime CreatedAt { get; set; }        // 第 5 列（UTC 时间）

    /// <summary>
    /// 获取东八区格式的记录日期（仅日期）
    /// </summary>
    public string RecordDateCst => RecordDate.AddHours(8).ToString("yyyy-MM-dd");
}

/// <summary>
/// B01_DELTA 长线新增实体（7 列）
/// </summary>
[Table("b01_delta")]
public class B01DeltaStock
{
    [Key]
    [Column("id")]
    public int Id { get; set; }                    // 第 1 列

    [Column("stock_code")]
    public string StockCode { get; set; } = string.Empty;  // 第 2 列

    [Column("stock_name")]
    public string StockName { get; set; } = string.Empty;  // 第 3 列

    [Column("entry_date")]
    public DateTime? EntryDate { get; set; }       // 第 4 列（UTC 时间）

    [Column("buy_point")]
    public decimal? BuyPoint { get; set; }         // 第 5 列

    [Column("record_date")]
    public DateTime RecordDate { get; set; }       // 第 6 列（UTC 时间）

    [Column("created_at")]
    public DateTime CreatedAt { get; set; }        // 第 7 列（UTC 时间）

    /// <summary>
    /// 获取东八区格式的入选日期（仅日期）
    /// </summary>
    public string EntryDateCst => EntryDate?.AddHours(8).ToString("yyyy-MM-dd") ?? "";

    /// <summary>
    /// 获取东八区格式的记录日期（仅日期）
    /// </summary>
    public string RecordDateCst => RecordDate.AddHours(8).ToString("yyyy-MM-dd");
}

/// <summary>
/// B02 长线日报实体（5 列）
/// </summary>
[Table("b02")]
public class B02Stock
{
    [Key]
    [Column("id")]
    public int Id { get; set; }                    // 第 1 列

    [Column("stock_code")]
    public string StockCode { get; set; } = string.Empty;  // 第 2 列

    [Column("stock_name")]
    public string StockName { get; set; } = string.Empty;  // 第 3 列

    [Column("record_date")]
    public DateTime RecordDate { get; set; }       // 第 4 列（UTC 时间）

    [Column("created_at")]
    public DateTime CreatedAt { get; set; }        // 第 5 列（UTC 时间）

    /// <summary>
    /// 获取东八区格式的记录日期（仅日期）
    /// </summary>
    public string RecordDateCst => RecordDate.AddHours(8).ToString("yyyy-MM-dd");
}

/// <summary>
/// B02_DELTA 长线新增实体（7 列）
/// </summary>
[Table("b02_delta")]
public class B02DeltaStock
{
    [Key]
    [Column("id")]
    public int Id { get; set; }                    // 第 1 列

    [Column("stock_code")]
    public string StockCode { get; set; } = string.Empty;  // 第 2 列

    [Column("stock_name")]
    public string StockName { get; set; } = string.Empty;  // 第 3 列

    [Column("entry_date")]
    public DateTime? EntryDate { get; set; }       // 第 4 列（UTC 时间）

    [Column("buy_point")]
    public decimal? BuyPoint { get; set; }         // 第 5 列

    [Column("record_date")]
    public DateTime RecordDate { get; set; }       // 第 6 列（UTC 时间）

    [Column("created_at")]
    public DateTime CreatedAt { get; set; }        // 第 7 列（UTC 时间）

    /// <summary>
    /// 获取东八区格式的入选日期（仅日期）
    /// </summary>
    public string EntryDateCst => EntryDate?.AddHours(8).ToString("yyyy-MM-dd") ?? "";

    /// <summary>
    /// 获取东八区格式的记录日期（仅日期）
    /// </summary>
    public string RecordDateCst => RecordDate.AddHours(8).ToString("yyyy-MM-dd");
}

/// <summary>
/// BA1 短线日报实体（5 列）
/// </summary>
[Table("ba1")]
public class BA1Stock
{
    [Key]
    [Column("id")]
    public int Id { get; set; }                    // 第 1 列

    [Column("stock_code")]
    public string StockCode { get; set; } = string.Empty;  // 第 2 列

    [Column("stock_name")]
    public string StockName { get; set; } = string.Empty;  // 第 3 列

    [Column("record_date")]
    public DateTime RecordDate { get; set; }       // 第 4 列（UTC 时间）

    [Column("created_at")]
    public DateTime CreatedAt { get; set; }        // 第 5 列（UTC 时间）

    /// <summary>
    /// 获取东八区格式的记录日期（仅日期）
    /// </summary>
    public string RecordDateCst => RecordDate.AddHours(8).ToString("yyyy-MM-dd");
}

/// <summary>
/// BA1_DELTA 短线新增实体（7 列）
/// </summary>
[Table("ba1_delta")]
public class BA1DeltaStock
{
    [Key]
    [Column("id")]
    public int Id { get; set; }                    // 第 1 列

    [Column("stock_code")]
    public string StockCode { get; set; } = string.Empty;  // 第 2 列

    [Column("stock_name")]
    public string StockName { get; set; } = string.Empty;  // 第 3 列

    [Column("entry_date")]
    public DateTime? EntryDate { get; set; }       // 第 4 列（UTC 时间）

    [Column("buy_point")]
    public decimal? BuyPoint { get; set; }         // 第 5 列

    [Column("record_date")]
    public DateTime RecordDate { get; set; }       // 第 6 列（UTC 时间）

    [Column("created_at")]
    public DateTime CreatedAt { get; set; }        // 第 7 列（UTC 时间）

    /// <summary>
    /// 获取东八区格式的入选日期（仅日期）
    /// </summary>
    public string EntryDateCst => EntryDate?.AddHours(8).ToString("yyyy-MM-dd") ?? "";

    /// <summary>
    /// 获取东八区格式的记录日期（仅日期）
    /// </summary>
    public string RecordDateCst => RecordDate.AddHours(8).ToString("yyyy-MM-dd");
}

/// <summary>
/// BA2 短线日报实体（5 列）
/// </summary>
[Table("ba2")]
public class BA2Stock
{
    [Key]
    [Column("id")]
    public int Id { get; set; }                    // 第 1 列

    [Column("stock_code")]
    public string StockCode { get; set; } = string.Empty;  // 第 2 列

    [Column("stock_name")]
    public string StockName { get; set; } = string.Empty;  // 第 3 列

    [Column("record_date")]
    public DateTime RecordDate { get; set; }       // 第 4 列（UTC 时间）

    [Column("created_at")]
    public DateTime CreatedAt { get; set; }        // 第 5 列（UTC 时间）

    /// <summary>
    /// 获取东八区格式的记录日期（仅日期）
    /// </summary>
    public string RecordDateCst => RecordDate.AddHours(8).ToString("yyyy-MM-dd");
}

/// <summary>
/// BA2_DELTA 短线新增实体（7 列）
/// </summary>
[Table("ba2_delta")]
public class BA2DeltaStock
{
    [Key]
    [Column("id")]
    public int Id { get; set; }                    // 第 1 列

    [Column("stock_code")]
    public string StockCode { get; set; } = string.Empty;  // 第 2 列

    [Column("stock_name")]
    public string StockName { get; set; } = string.Empty;  // 第 3 列

    [Column("entry_date")]
    public DateTime? EntryDate { get; set; }       // 第 4 列（UTC 时间）

    [Column("buy_point")]
    public decimal? BuyPoint { get; set; }         // 第 5 列

    [Column("record_date")]
    public DateTime RecordDate { get; set; }       // 第 6 列（UTC 时间）

    [Column("created_at")]
    public DateTime CreatedAt { get; set; }        // 第 7 列（UTC 时间）

    /// <summary>
    /// 获取东八区格式的入选日期（仅日期）
    /// </summary>
    public string EntryDateCst => EntryDate?.AddHours(8).ToString("yyyy-MM-dd") ?? "";

    /// <summary>
    /// 获取东八区格式的记录日期（仅日期）
    /// </summary>
    public string RecordDateCst => RecordDate.AddHours(8).ToString("yyyy-MM-dd");
}

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
        // B01
        modelBuilder.Entity<B01Stock>(entity =>
        {
            entity.ToTable("b01");
            entity.HasKey(e => e.Id);
            entity.Property(e => e.StockCode).HasColumnName("stock_code").IsRequired();
            entity.Property(e => e.StockName).HasColumnName("stock_name").IsRequired();
            entity.Property(e => e.RecordDate).HasColumnName("record_date").IsRequired();
            entity.Property(e => e.CreatedAt).HasColumnName("created_at").IsRequired();
        });

        // B01_DELTA
        modelBuilder.Entity<B01DeltaStock>(entity =>
        {
            entity.ToTable("b01_delta");
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.StockCode).HasColumnName("stock_code").IsRequired();
            entity.Property(e => e.StockName).HasColumnName("stock_name").IsRequired();
            entity.Property(e => e.EntryDate).HasColumnName("entry_date");
            entity.Property(e => e.BuyPoint).HasColumnName("buy_point");
            entity.Property(e => e.RecordDate).HasColumnName("record_date").IsRequired();
            entity.Property(e => e.CreatedAt).HasColumnName("created_at").IsRequired();
        });

        // B02
        modelBuilder.Entity<B02Stock>(entity =>
        {
            entity.ToTable("b02");
            entity.HasKey(e => e.Id);
            entity.Property(e => e.StockCode).HasColumnName("stock_code").IsRequired();
            entity.Property(e => e.StockName).HasColumnName("stock_name").IsRequired();
            entity.Property(e => e.RecordDate).HasColumnName("record_date").IsRequired();
            entity.Property(e => e.CreatedAt).HasColumnName("created_at").IsRequired();
        });

        // B02_DELTA
        modelBuilder.Entity<B02DeltaStock>(entity =>
        {
            entity.ToTable("b02_delta");
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.StockCode).HasColumnName("stock_code").IsRequired();
            entity.Property(e => e.StockName).HasColumnName("stock_name").IsRequired();
            entity.Property(e => e.EntryDate).HasColumnName("entry_date");
            entity.Property(e => e.BuyPoint).HasColumnName("buy_point");
            entity.Property(e => e.RecordDate).HasColumnName("record_date").IsRequired();
            entity.Property(e => e.CreatedAt).HasColumnName("created_at").IsRequired();
        });

        // BA1
        modelBuilder.Entity<BA1Stock>(entity =>
        {
            entity.ToTable("ba1");
            entity.HasKey(e => e.Id);
            entity.Property(e => e.StockCode).HasColumnName("stock_code").IsRequired();
            entity.Property(e => e.StockName).HasColumnName("stock_name").IsRequired();
            entity.Property(e => e.RecordDate).HasColumnName("record_date").IsRequired();
            entity.Property(e => e.CreatedAt).HasColumnName("created_at").IsRequired();
        });

        // BA1_DELTA
        modelBuilder.Entity<BA1DeltaStock>(entity =>
        {
            entity.ToTable("ba1_delta");
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.StockCode).HasColumnName("stock_code").IsRequired();
            entity.Property(e => e.StockName).HasColumnName("stock_name").IsRequired();
            entity.Property(e => e.EntryDate).HasColumnName("entry_date");
            entity.Property(e => e.BuyPoint).HasColumnName("buy_point");
            entity.Property(e => e.RecordDate).HasColumnName("record_date").IsRequired();
            entity.Property(e => e.CreatedAt).HasColumnName("created_at").IsRequired();
        });

        // BA2
        modelBuilder.Entity<BA2Stock>(entity =>
        {
            entity.ToTable("ba2");
            entity.HasKey(e => e.Id);
            entity.Property(e => e.StockCode).HasColumnName("stock_code").IsRequired();
            entity.Property(e => e.StockName).HasColumnName("stock_name").IsRequired();
            entity.Property(e => e.RecordDate).HasColumnName("record_date").IsRequired();
            entity.Property(e => e.CreatedAt).HasColumnName("created_at").IsRequired();
        });

        // BA2_DELTA
        modelBuilder.Entity<BA2DeltaStock>(entity =>
        {
            entity.ToTable("ba2_delta");
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.StockCode).HasColumnName("stock_code").IsRequired();
            entity.Property(e => e.StockName).HasColumnName("stock_name").IsRequired();
            entity.Property(e => e.EntryDate).HasColumnName("entry_date");
            entity.Property(e => e.BuyPoint).HasColumnName("buy_point");
            entity.Property(e => e.RecordDate).HasColumnName("record_date").IsRequired();
            entity.Property(e => e.CreatedAt).HasColumnName("created_at").IsRequired();
        });
    }
}
