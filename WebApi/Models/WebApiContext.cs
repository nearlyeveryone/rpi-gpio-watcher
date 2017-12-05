using Microsoft.EntityFrameworkCore;
using WebApi.Models.Gpio;

namespace WebApi.Models
{
    public class WebApiContext : DbContext
    {
        public WebApiContext(DbContextOptions<WebApiContext> options): base(options)
        {

        }

        public DbSet<ControlModel> ControlModels {get; set; }
    }
}