using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Caching.Memory;

namespace evernote_blog.Controllers
{
    public class CacheController : Controller
    {
        private IMemoryCache _cache;
        public CacheController(IMemoryCache cache)
        {
            _cache = cache;
        }
       
    }
}