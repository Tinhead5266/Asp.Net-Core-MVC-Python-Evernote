using evernote_blog.Models;
using System.Collections.Generic;

namespace evernote_blog.DataAccess.Interface
{
    interface INoteInfoDb
    {
        /// <summary>
        /// 分页加载笔记
        /// </summary>
        /// <param name="count"></param>
        /// <param name="pageIndexOut"></param>
        /// <param name="type"></param>
        /// <param name="page"></param>
        /// <param name="pageSize"></param>
        /// <param name="classifyId"></param>
        /// <param name="searchText"></param>
        /// <param name="createTime"></param>
        /// <returns></returns>
        List<NoteInfo> GetNoteInfoByPage(out int count, out int pageIndexOut, string type = "", int page = 0, int pageSize = 10, int classifyId = 0, string searchText = "", long createTime = 0);

        /// <summary>
        /// 根据笔记Evernote编号获取笔记
        /// </summary>
        /// <param name="guid"></param>
        /// <returns></returns>
        NoteInfo GetNoteInfoByGuid(string guid);

        /// <summary>
        /// 根据笔记名称获取笔记（）模糊查询
        /// </summary>
        /// <param name="title"></param>
        /// <returns></returns>
        List<NoteInfo> GetNoteInfoByTitle(string title);

        /// <summary>
        /// 获取笔记总数
        /// </summary>
        /// <returns></returns>
        int GetNoteInfoCount();

        /// <summary>
        /// 获取有笔记的分类编号
        /// </summary>
        /// <returns></returns>
        List<ShowNoteClassifyInfo> GetClassifyIdList();
    }
}
