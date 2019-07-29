using Microsoft.EntityFrameworkCore;

namespace evernote_blog.Models
{
    public class DataContext : DbContext
    {
        public DataContext(DbContextOptions<DataContext> options)
            : base(options)
        {
        }

        public DbSet<NoteInfo> NoteData { get; set; }

        public DbSet<ClassifyInfo> ClassifyData { get; set; }
    }
}
