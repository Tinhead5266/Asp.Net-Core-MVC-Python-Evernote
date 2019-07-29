using evernote_blog.DataAccess.Implement;
using evernote_blog.Models;
using Microsoft.Extensions.Caching.Memory;
using System.Collections.Generic;

namespace evernote_blog.Common
{
    public class CacheUnit
    {
        static readonly MemoryCache Cache = null;

        public static List<ClassifyInfo> GetClassifyInfos()
        {
            var key = "GetClassifyInfos";
            var cacheData = Cache.Get(key);
            List<ClassifyInfo> data = null;
            if (cacheData == null)
            {
                ClassifyInfoDb classifyInfoDb = new ClassifyInfoDb(CommonUnit.Context);
                data = classifyInfoDb.GetAllClassifyInfo();
                Cache.Set(key, data);
            }
            else
            {
                data = (List<ClassifyInfo>)cacheData;
            }

            return data;
        }

    }
}
