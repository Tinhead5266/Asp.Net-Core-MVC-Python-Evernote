using System.ComponentModel.DataAnnotations.Schema;

namespace evernote_blog.Models
{
    [Table("note_info")]
    public class NoteInfo
    {
        /// <summary>
        /// 编号
        /// </summary>
        [Column("id")]
        public int Id { get; set; }

        /// <summary>
        /// 标题
        /// </summary>
        [Column("title")]
        public string Title { get; set; }

        /// <summary>
        /// 分类编号
        /// </summary>
        [Column("classify_id")]
        public int ClassifyId { get; set; }

        /// <summary>
        /// 是否是博客文章
        /// </summary>
        [Column("is_blog")]
        public int IsBlog { get; set; }

        /// <summary>
        /// 标签
        /// </summary>
        [Column("tags")]
        public string Tags { get; set; }

        /// <summary>
        /// 文章内容文件名称
        /// </summary>
        [Column("content")]
        public string Content { get; set; }

        /// <summary>
        /// 文章内容摘要
        /// </summary>
        [Column("content_snippet")]
        public string ContentSnippet { get; set; }

        /// <summary>
        /// 创建时间
        /// </summary>
        [Column("create_time")]
        public long CreateTime { get; set; }

        /// <summary>
        /// 修改时间
        /// </summary>
        [Column("update_time")]
        public long UpdateTime { get; set; }

        /// <summary>
        /// 笔记Evernote编号
        /// </summary>
        [Column("note_guid")]
        public string NoteGuid { get; set; }

        ///// <summary>
        ///// 分类
        ///// </summary>
        //public ClassifyInfo ClassifyInfo { get; set; }

    }

    public class ShowNoteClassifyInfo
    {
        /// <summary>
        /// 分类编号
        /// </summary>
        public int ClassifyId { get; set; }


        /// <summary>
        /// 分类名称
        /// </summary>
        public string ClassifyName { get; set; }

        /// <summary>
        /// 笔记本数
        /// </summary>
        public int NoteCount { get; set; }
    }
}
