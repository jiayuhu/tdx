using Microsoft.AspNetCore.Mvc.RazorPages;
using web.Data;
using web.Services;

namespace web.Pages.Index;

public class BA1Model : PageModel
{
    private readonly StockService _stockService;
    public BA1Model(StockService stockService) => _stockService = stockService;

    public List<BA1Stock> BA1Stocks { get; private set; } = new();
    public List<BA1DeltaStock> BA1DeltaStocks { get; private set; } = new();
    public int BA1Count { get; private set; }
    public int BA1DeltaCount { get; private set; }

    public async Task OnGetAsync()
    {
        BA1Stocks = await _stockService.GetBA1DataAsync();
        BA1DeltaStocks = await _stockService.GetBA1DeltaDataAsync();
        BA1Count = BA1Stocks.Count;
        BA1DeltaCount = BA1DeltaStocks.Count;
    }
}
