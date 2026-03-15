using Microsoft.EntityFrameworkCore;
using web.Data;
using web.Services;

var builder = WebApplication.CreateBuilder(args);

// 日志配置
builder.Logging.ClearProviders();
builder.Logging.AddConsole();
builder.Logging.SetMinimumLevel(
    builder.Environment.IsDevelopment() ? LogLevel.Debug : LogLevel.Information);

// 数据库连接
var connStr = builder.Configuration.GetConnectionString("DefaultConnection");

if (string.IsNullOrEmpty(connStr))
{
    var dbPath = Path.Combine(builder.Environment.ContentRootPath, "..", "data", "quant.db");
    connStr = $"Data Source={dbPath}";
}

// 添加服务
builder.Services.AddRazorPages();

builder.Services.AddDbContextFactory<TdxDbContext>(options =>
    options.UseSqlite(connStr));

builder.Services.AddSingleton<StockService>();

var app = builder.Build();

// 启动日志（使用 ILogger）
var logger = app.Services.GetRequiredService<ILogger<Program>>();
logger.LogInformation("工作目录：{Dir}", Environment.CurrentDirectory);
logger.LogInformation("连接字符串：{ConnStr}", connStr);

// 配置 HTTP 管道
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error");
    app.UseHsts();
}

app.UseHttpsRedirection();
app.UseStaticFiles();

app.UseRouting();

app.UseAuthorization();

// 默认路由重定向到 Home 页面
app.MapGet("/", () => Results.Redirect("/Index"));

app.MapRazorPages();

app.Run();
