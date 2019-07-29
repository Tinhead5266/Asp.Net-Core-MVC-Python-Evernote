using evernote_blog.Common;
using evernote_blog.DataAccess.Interface;
using evernote_blog.Models;
using Microsoft.EntityFrameworkCore;
using System;
using System.Collections.Generic;
using System.Linq;

namespace evernote_blog.DataAccess.Implement
{
    public class NoteInfoDb : INoteInfoDb
    {
        public DataContext Context;

        public NoteInfoDb(DataContext context)
        {
            Context = context;
        }

        /// <summary>
        /// 获取有笔记的分类编号
        /// </summary>
        /// <returns></returns>
        public List<ShowNoteClassifyInfo> GetClassifyIdList()
        {
            var classifyGroupList = Context.NoteData.GroupBy(p => p.ClassifyId);

            var showNoteClassifyInfos = new List<ShowNoteClassifyInfo>();

            foreach (var classifyGroupItem in classifyGroupList)
            {
                var classifyId = classifyGroupItem.Key;
                showNoteClassifyInfos.Add(new ShowNoteClassifyInfo
                {
                    ClassifyId = classifyId,
                    NoteCount = classifyGroupItem.Count(),
                    ClassifyName = CommonUnit.GetClassifyName(classifyId)
                });
            }

            return showNoteClassifyInfos.OrderByDescending(p => p.NoteCount).ToList();

        }

        /// <summary>
        /// 根据笔记Evernote编号获取笔记
        /// </summary>
        /// <param name="guid"></param>
        /// <returns></returns>
        public NoteInfo GetNoteInfoByGuid(string guid)
        {
            return Context.NoteData.Single(p => p.NoteGuid == guid);
        }

        /// <summary>
        /// 分页加载笔记
        /// </summary>
        /// <param name="pageSum"></param>
        /// <param name="type"></param>
        /// <param name="pageIndexOut"></param>
        /// <param name="pageIndex"></param>
        /// <param name="pageSize"></param>
        /// <param name="classifyId"></param>
        /// <param name="searchText"></param>
        /// <returns></returns>
        public List<NoteInfo> GetNoteInfoByPage(out int pageSum, out int pageIndexOut, string type = "", int pageIndex = 1, int pageSize = 8, int classifyId = 0, string searchText = "")
        {

            var dbData = Context.NoteData.OrderByDescending(p => p.UpdateTime).Where(p => true);

            if (classifyId > 0)
            {
                dbData = dbData.Where(p => p.ClassifyId == classifyId);
            }

            if (!string.IsNullOrWhiteSpace(searchText))
            {
                dbData = dbData.Where(p => p.Title.Contains(searchText));
            }
            var count = dbData.Count();
            pageSum = (int)Math.Ceiling(count / (double)pageSize);

            switch (type)
            {
                case "first":
                    pageIndex = 1;
                    break;

                case "end":
                    pageIndex = pageSum;
                    break;

                case "last":
                    pageIndex--;
                    pageIndex = pageIndex <= 0 ? 1 : pageIndex;
                    break;

                case "next":
                    pageIndex++;
                    if (pageSum > 0)
                    {
                        pageIndex = pageIndex > pageSum ? pageSum : pageIndex;
                    }
                    else
                    {
                        pageIndex = 1;
                    }
                    break;

                case "skip":
                    if (pageSum > 0)
                    {
                        pageIndex = pageIndex > pageSum ? pageSum : pageIndex <= 0 ? 1 : pageIndex;
                    }
                    else
                    {
                        pageIndex = 1;
                    }
                    break;

                case "className":

                    break;
                case "search":
                    if (string.IsNullOrWhiteSpace(searchText))
                    {
                        pageIndex = 1;
                    }
                    break;
                default:
                    pageIndex = 1;
                    break;
            }

            var noteData = dbData.Skip((pageIndex - 1) * pageSize).Take(pageSize).ToList();
            pageIndexOut = pageIndex;
            return noteData;
        }

        /// <summary>
        /// 根据笔记名称获取笔记（）模糊查询
        /// </summary>
        /// <param name="title"></param>
        /// <returns></returns>
        public List<NoteInfo> GetNoteInfoByTitle(string title)
        {
            return Context.NoteData.Where(p => EF.Functions.Like(p.Title, $"%{title}%")).ToList();
        }

        /// <summary>
        /// 获取笔记总数
        /// </summary>
        /// <returns></returns>
        public int GetNoteInfoCount()
        {
            return Context.NoteData.Count();
        }
    }
}
