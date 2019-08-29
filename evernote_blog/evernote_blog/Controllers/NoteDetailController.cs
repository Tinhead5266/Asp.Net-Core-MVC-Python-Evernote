using evernote_blog.Common;
using evernote_blog.DataAccess.Implement;
using evernote_blog.Models;
using Microsoft.AspNetCore.Mvc;

namespace evernote_blog.Controllers
{
    public class NoteDetailController : Controller
    {
        private readonly NoteInfoDb _noteInfoDb;

        public NoteDetailController(DataContext context)
        {
            CommonUnit.Context = context;
            _noteInfoDb = new NoteInfoDb(context);
        }

        public IActionResult Index(string guid)
        {
            if (string.IsNullOrWhiteSpace(guid))
            {
                return RedirectToAction("Index", "Error");
            }
            ViewBag.NoteInfo = _noteInfoDb.GetNoteInfoByGuid(guid);
            ViewBag.ShowNoteClassifyInfo = _noteInfoDb.GetClassifyIdList();
            return View();
        }
    }
}