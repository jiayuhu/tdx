using Microsoft.EntityFrameworkCore;
using web.Data;
using web.Services;
using System.IO;

var builder = WebApplication.CreateBuilder(args);

// 添加日志 - 保留 Console 输出
builder.Logging.ClearProviders();
builder.Logging.AddConsole();
builder.Logging.SetMinimumLevel(LogLevel.Debug);

// 打印配置信息
Console.WriteLine("=== 启动配置 ===");
Console.WriteLine($"工作目录：{Environment.CurrentDirectory}");
Console.WriteLine($"配置文件路径：{builder.Environment.ContentRootPath}");

// 从配置文件读取数据库连接
var connStr = builder.Configuration.GetConnectionString("DefaultConnection");

// 如果配置文件没有连接字符串，使用相对路径构建
if (string.IsNullOrEmpty(connStr))
{
    var dbPath = Path.Combine(builder.Environment.ContentRootPath, "..", "data", "quant.db");
    connStr = $"Data Source={dbPath}";
    Console.WriteLine($"使用相对路径构建连接字符串：{connStr}");
}
else
{
    Console.WriteLine($"连接字符串：{connStr}");
}
Console.WriteLine("================");

// 添加服务
builder.Services.AddRazorPages();

// 配置 EF Core
builder.Services.AddDbContextFactory<TdxDbContext>(options =>
    options.UseSqlite(connStr));

// 注册数据服务
builder.Services.AddSingleton<StockService>();

var app = builder.Build();

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
