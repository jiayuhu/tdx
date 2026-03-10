using Microsoft.AspNetCore.Mvc.RazorPages;
using web.Data;
using web.Services;

namespace web.Pages.Index;

public class B02Model : PageModel
{
    private readonly StockService _stockService;
    public B02Model(StockService stockService) => _stockService = stockService;

    public List<B02Stock> B02Stocks { get; private set; } = new();
    public List<B02DeltaStock> B02DeltaStocks { get; private set; } = new();
    public int B02Count { get; private set; }
    public int B02DeltaCount { get; private set; }

    public async Task OnGetAsync()
    {
        B02Stocks = await _stockService.GetB02DataAsync();
        B02DeltaStocks = await _stockService.GetB02DeltaDataAsync();
        B02Count = B02Stocks.Count;
        B02DeltaCount = B02DeltaStocks.Count;
    }
}
