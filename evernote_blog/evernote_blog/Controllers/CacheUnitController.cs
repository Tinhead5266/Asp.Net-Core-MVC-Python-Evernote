using evernote_blog.DataAccess.Implement;
using evernote_blog.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Caching.Memory;
using System.Collections.Generic;

namespace evernote_blog.Controllers
{

    public class CacheUnitController : Controller
    {
        private readonly NoteInfoDb _noteInfoDb;
        private readonly ClassifyInfoDb _classifyInfo;
        static readonly IMemoryCache Cache = null;

        public CacheUnitController(DataContext context)
        {
            _noteInfoDb = new NoteInfoDb(context);
            _classifyInfo = new ClassifyInfoDb(context);
        }

        public List<ClassifyInfo> GetClassifyInfos()
        {
            var data = Cache.Get<List<ClassifyInfo>>("GetClassifyInfos");
            if (data == null)
            {
                data = _classifyInfo.GetAllClassifyInfo();
            }
            return data;
        }
    }
}