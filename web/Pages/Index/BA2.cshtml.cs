using Microsoft.AspNetCore.Mvc.RazorPages;
using web.Data;
using web.Services;

namespace web.Pages.Index;

public class BA2Model : PageModel
{
    private readonly StockService _stockService;
    public BA2Model(StockService stockService) => _stockService = stockService;

    public List<BA2Stock> BA2Stocks { get; private set; } = new();
    public List<BA2DeltaStock> BA2DeltaStocks { get; private set; } = new();
    public int BA2Count { get; private set; }
    public int BA2DeltaCount { get; private set; }

    public async Task OnGetAsync()
    {
        BA2Stocks = await _stockService.GetBA2DataAsync();
        BA2DeltaStocks = await _stockService.GetBA2DeltaDataAsync();
        BA2Count = BA2Stocks.Count;
        BA2DeltaCount = BA2DeltaStocks.Count;
    }
}
