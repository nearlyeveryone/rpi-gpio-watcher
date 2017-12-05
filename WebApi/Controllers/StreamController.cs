using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Http;
using System.IO;
using Microsoft.Extensions.FileProviders;
using Microsoft.AspNetCore.Authorization;
using WebApi.Models;

namespace WebApi.Controllers
{
    [Route("[controller]")]
    [AllowAnonymous]
    public class StreamController : Controller
    {
        private ValidIps _ipService;

        public StreamController(ValidIps ipService)
        {
            _ipService = ipService;
        }

        [HttpGet("{filename}")]
        public async Task<IActionResult> Download(string filename)
        {
            string ip = HttpContext.Connection.RemoteIpAddress.ToString();
            if(_ipService.Ips.ContainsKey(ip))
            {
                if(_ipService.Ips[ip].AddMinutes(600) < DateTime.Now)
                {
                    _ipService.Ips.Remove(ip);
                    return Unauthorized();
                }

                string basePath = "/stream/hls";
                if(filename == null)
                    return Content("no path given");
                string path = Path.Combine(basePath, filename);
                if(!path.StartsWith(basePath))
                {
                    return Content("invalid filename");
                }
                MemoryStream memory = new MemoryStream();
                using (FileStream stream = new FileStream(path,FileMode.Open))
                {
                    await stream.CopyToAsync(memory);
                }
                memory.Position = 0;
                return File(memory, GetContentType(path), Path.GetFileName(path));
            }
            System.Console.Out.WriteLine("FAIL: current ip: " + ip);
            foreach(var ipp in _ipService.Ips.Keys)
            {
                System.Console.Out.WriteLine("ipp: " + ipp);
            }
            return Unauthorized();
        }

        private string GetContentType(string path)
        {
            var types = GetMimeTypes();
            var ext = Path.GetExtension(path).ToLowerInvariant();
            return types[ext];
        }

        private Dictionary<string, string> GetMimeTypes()
        {
            return new Dictionary<string, string>
            {
                {".mpd", "application/dash+xml"},
                {".m3u8", "application/vnd.apple.mpegurl"},
                {".ts", "video/mp2t"}
            };
        }
    }
}