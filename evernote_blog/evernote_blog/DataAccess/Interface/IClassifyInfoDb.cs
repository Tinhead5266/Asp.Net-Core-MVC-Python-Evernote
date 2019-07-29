using evernote_blog.Models;
using System.Collections.Generic;

namespace evernote_blog.DataAccess.Interface
{
    interface IClassifyInfoDb
    {
        /// <summary>
        /// 加载所有分类
        /// </summary>
        /// <returns></returns>
        List<ClassifyInfo> GetAllClassifyInfo();
    }
}
