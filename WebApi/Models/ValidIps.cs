using System;
using System.Collections.Generic;

namespace WebApi.Models
{
    public class ValidIps
    {
        public Dictionary<string,DateTime> Ips { get; set; }
        public ValidIps()
        {
            Ips = new Dictionary<string,DateTime>();
        }
    }
}