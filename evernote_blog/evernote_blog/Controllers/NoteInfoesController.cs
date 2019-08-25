using evernote_blog.Common;
using evernote_blog.DataAccess.Implement;
using evernote_blog.Models;
using Microsoft.AspNetCore.Mvc;
using System;
using System.Linq;

namespace evernote_blog.Controllers
{
    public class NoteInfoesController : Controller
    {
        private readonly NoteInfoDb _noteInfoDb;

        private static int _classifyId = 0;
        private static int _pageIndex = 1;
        private static string _searchText = string.Empty;
        private static long _createTime = 1;
        private int _pageSum = 0;
        private int _pageSize = 10;

        public NoteInfoesController(DataContext context)
        {
            CommonUnit.Context = context;
            _noteInfoDb = new NoteInfoDb(context);
            var count = _noteInfoDb.GetNoteInfoCount();
            _pageSum = (int)Math.Ceiling(count / (double)_pageSize);

        }

        // GET: NoteInfoes
        //[ResponseCache(Duration = 600)]
        public IActionResult Index(string type = "", int pageIndex = 0, int classifyId = 0, string searchText = "", long createTime = 0)
        {

            switch (type)
            {
                case "first":
                case "end":
                case "last":
                case "next":
                case "skip":
                    _classifyId = classifyId > 0 ? classifyId : _classifyId;
                    _pageIndex = pageIndex > 0 ? pageIndex : _pageIndex;
                    _searchText = !string.IsNullOrWhiteSpace(searchText) ? searchText : _searchText;
                    _createTime = createTime > 0 ? createTime : _createTime;
                    break;

                case "search":
                case "className":
                case "createTime":
                    _classifyId = 0;
                    _pageIndex = 1;
                    _createTime = 0;

                    switch (type)
                    {
                        case "search":
                            _searchText = !string.IsNullOrWhiteSpace(searchText) ? searchText : _searchText;
                            break;
                        case "className":
                            _classifyId = classifyId > 0 ? classifyId : _classifyId;
                            break;
                        case "createTime":
                            _createTime = createTime > 0 ? createTime : _createTime;
                            break;
                    }
                    break;
                default:
                    _classifyId = 0;
                    _pageIndex = 1;
                    _searchText = string.Empty;
                    _createTime = 0;
                    break;
            }

            var n = 5;
            var data = _noteInfoDb.GetNoteInfoByPage(out var pageSum, out _pageIndex, type, _pageIndex, _pageSize, _classifyId, _searchText, _createTime);

            //banner博客数据
            ViewBag.BannerNoteInfo = _noteInfoDb.GetNewestNOteInfos();

            ViewBag.NoteInfo = data;
            ViewBag.PageIndex = _pageIndex;
            ViewBag.PageStrList = CommonUnit.GetPageStrList(pageSum, _pageIndex);
            ViewBag.ShowNoteClassifyInfo = _noteInfoDb.GetClassifyIdList();
            return View();
        }
    }
}
