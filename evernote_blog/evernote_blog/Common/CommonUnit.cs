using evernote_blog.DataAccess.Implement;
using evernote_blog.Models;
using System;
using System.Collections.Generic;
using System.Linq;

namespace evernote_blog.Common
{
    public class CommonUnit
    {
        public static DataContext Context;
        public static List<ClassifyInfo> ClassifyInfos;

        /// <summary>
        /// 获取分类名称
        /// </summary>
        /// <param name="classifyId"></param>
        /// <returns></returns>
        public static string GetClassifyName(int classifyId)
        {
            if (ClassifyInfos == null)
            {
                ClassifyInfos = new ClassifyInfoDb(Context).GetAllClassifyInfo();
            }
            return ClassifyInfos.First(p => p.Id == classifyId)?.ClassifyName ?? string.Empty;
        }

        /// <summary>
        /// 时间戳转化
        /// </summary>
        /// <returns></returns>
        public static string FormatTime(long timeStamp)
        {
            var start = new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc);
            var dateTime = start.AddMilliseconds(timeStamp).AddHours(8);
            return dateTime.ToString("yyyy-MM-dd");
        }

        public static string GetBlogImageStr()
        {
            var maxNum = 12;
            Random random = new Random();
            var n = random.Next(1, maxNum);
            return $"img/home-blog/blog-{n}.jpg";
        }

        /// <summary>
        /// 获取分页的页码
        /// </summary>
        /// <param name="pageSum"></param>
        /// <param name="pageIndex"></param>
        /// <returns></returns>
        public static List<string> GetPageStrList(int pageSum, int pageIndex)
        {
            var n = 7;
            var pageStrList = new List<string>();
            if (pageSum <= n)
            {
                for (int i = 1; i <= pageSum; i++)
                {
                    pageStrList.Add(i + "");
                }
            }
            else
            {
                var index = (int)Math.Ceiling(n / 2.00);
                var pageStart = pageSum - pageIndex;

                //当前页数在倒数index页内
                if (pageStart < index)
                {
                    pageStart = pageSum - n + 1;
                }
                else
                {
                    pageStart = pageIndex - index + 1;
                    pageStart = pageStart <= 0 ? 1 : pageStart;
                }

                for (int i = 0; i < n; i++)
                {
                    pageStrList.Add((pageStart + i) + "");
                }
            }

            return pageStrList;
        }


        public static List<ClassifyInfo> GetBlogShowClassifyInfos(List<int> classifyIds)
        {
            var classifyInfos = new List<ClassifyInfo>();
            if (ClassifyInfos == null)
            {
                ClassifyInfos = new ClassifyInfoDb(Context).GetAllClassifyInfo();
            }
            classifyInfos = ClassifyInfos.Where(p => classifyIds.Contains(p.Id)).ToList();


            return classifyInfos;
        }
    }
}
