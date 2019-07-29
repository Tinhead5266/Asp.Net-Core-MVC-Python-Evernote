using evernote_blog.DataAccess.Interface;
using evernote_blog.Models;
using System.Collections.Generic;
using System.Linq;

namespace evernote_blog.DataAccess.Implement
{
    public class ClassifyInfoDb : IClassifyInfoDb
    {
        public DataContext Context;

        public ClassifyInfoDb(DataContext context)
        {
            Context = context;
        }

        /// <summary>
        /// 加载所有分类
        /// </summary>
        /// <returns></returns>
        public List<ClassifyInfo> GetAllClassifyInfo()
        {
            return Context.ClassifyData.ToList();
        }
    }
}
