using System.ComponentModel.DataAnnotations.Schema;

namespace evernote_blog.Models
{
    [Table("classify_info")]
    public class ClassifyInfo
    {
        /// <summary>
        /// 编号
        /// </summary>
        [Column("id")]
        public int Id { get; set; }

        /// <summary>
        /// 标题
        /// </summary>
        [Column("classify_name")]
        public string ClassifyName { get; set; }

        /// <summary>
        /// 分类编号
        /// </summary>
        [Column("parent_id")]
        public int ParentId { get; set; }

        /// <summary>
        /// 分类Evernote编号
        /// </summary>
        [Column("guid")]
        public string Guid { get; set; }

    }
}

