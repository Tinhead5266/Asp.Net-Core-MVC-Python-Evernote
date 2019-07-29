using evernote_blog.Common;
using evernote_blog.DataAccess.Implement;
using evernote_blog.Models;
using Microsoft.AspNetCore.Mvc;
using System;

namespace evernote_blog.Controllers
{
    public class NoteInfoesController : Controller
    {
        private readonly NoteInfoDb _noteInfoDb;

        private static int _classifyId = 0;
        private static int _pageIndex = 1;
        private int _pageSum = 0;
        private int _pageSize = 2;

        public NoteInfoesController(DataContext context)
        {
            CommonUnit.Context = context;
            _noteInfoDb = new NoteInfoDb(context);
            var count = _noteInfoDb.GetNoteInfoCount();
            _pageSum = (int)Math.Ceiling(count / (double)_pageSize);

        }

        // GET: NoteInfoes
        //[ResponseCache(Duration = 600)]
        public IActionResult Index(string type = "", int pageIndex = 1, int classifyId = 0, string searchText = "")
        {
            _classifyId = classifyId > 0 ? classifyId : _classifyId;
            _pageIndex = pageIndex > 0 ? pageIndex : _pageIndex;
            var data = _noteInfoDb.GetNoteInfoByPage(out var pageSum, out _pageIndex, type, _pageIndex, _pageSize, _classifyId, searchText);
            ViewBag.NoteInfo = data;
            ViewBag.PageIndex = _pageIndex;
            ViewBag.PageStrList = CommonUnit.GetPageStrList(pageSum, _pageIndex);
            ViewBag.ShowNoteClassifyInfo = _noteInfoDb.GetClassifyIdList();
            return View();
        }
    }
}
