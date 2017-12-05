using Microsoft.AspNetCore.Mvc;
using WebApi.Models.Token;
using WebApi.Helpers;
using Microsoft.AspNetCore.Authorization;
using Newtonsoft.Json;
using System.IO;
using System;
using System.Collections.Generic;
using System.Security.Cryptography;
using Microsoft.AspNetCore.Cryptography.KeyDerivation;
using Microsoft.Extensions.Configuration;

using WebApi.Models;

namespace WebApi.Controllers
{
    [Route("[controller]")]
    [AllowAnonymous]
    public class TokenController : Controller
    {
        private IConfiguration _configuration;
        private ValidIps _ipService;
        public TokenController(IConfiguration configuration, ValidIps ipService)
        {
            _ipService = ipService;
            _configuration = configuration;
        }

        [HttpPost]
        public IActionResult Create([FromBody]LoginInputModel inputModel)
        {
            if (!checkPassword(inputModel.Password))
                return Unauthorized();
            string ip = HttpContext.Connection.RemoteIpAddress.ToString();
            if(_ipService.Ips.ContainsKey(ip))
            {
                _ipService.Ips[ip] = DateTime.Now;
            }
            else{
                _ipService.Ips.Add(ip, DateTime.Now);
            }

            var token = new JwtTokenBuilder()
                                .AddSecurityKey(JwtSecurityKey.Create(_configuration["jwtsecret"]))
                                .AddSubject("admin")
                                .AddIssuer("nearlyeveryone")
                                .AddAudience("nearlyeveryone")
                                .AddClaim("admin", "admin")
                                .AddExpiry(600)
                                .Build();

            return Json(token);
        }

        private bool checkPassword(string password)
        {
            string json = System.IO.File.ReadAllText("password.json");
            Dictionary<string, string> convertedJson = JsonConvert.DeserializeObject<Dictionary<string, string>>(json);

            byte[] salt = new byte[128 / 8];

            if(convertedJson["hashed"] == "false")
            {
                using (var rng = RandomNumberGenerator.Create())
                {
                    rng.GetBytes(salt);
                }
            }
            else{
                salt = Convert.FromBase64String(convertedJson["salt"]);
            }
            // derive a 256-bit subkey (use HMACSHA1 with 10,000 iterations)
            string hashed = Convert.ToBase64String(KeyDerivation.Pbkdf2(
                password: password,
                salt: salt,
                prf: KeyDerivationPrf.HMACSHA1,
                iterationCount: 10000,
                numBytesRequested: 256 / 8));

            if(convertedJson["hashed"] == "false")
            {
                convertedJson["hashed"] = "true";
                convertedJson["value"] = hashed;
                convertedJson["salt"] = Convert.ToBase64String(salt);
                System.IO.File.WriteAllText("password.json", JsonConvert.SerializeObject(convertedJson));

                return true;
            } 
            else if(convertedJson["value"] == hashed)
            {
                return true;
            }
            else{
                return false;
            }
        }
    }
}