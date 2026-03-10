using Microsoft.AspNetCore.Mvc.RazorPages;
using web.Data;
using web.Services;

namespace web.Pages.Index;

public class B01Model : PageModel
{
    private readonly StockService _stockService;

    public B01Model(StockService stockService)
    {
        _stockService = stockService;
    }

    public List<B01Stock> B01Stocks { get; private set; } = new();
    public List<B01DeltaStock> B01DeltaStocks { get; private set; } = new();
    public int B01Count { get; private set; }
    public int B01DeltaCount { get; private set; }

    public async Task OnGetAsync()
    {
        B01Stocks = await _stockService.GetB01DataAsync();
        B01DeltaStocks = await _stockService.GetB01DeltaDataAsync();
        B01Count = B01Stocks.Count;
        B01DeltaCount = B01DeltaStocks.Count;
    }
}
