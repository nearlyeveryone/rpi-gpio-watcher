using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Http;
using System.IO;
using Microsoft.Extensions.FileProviders;
using Microsoft.AspNetCore.Authorization;
using Newtonsoft.Json;

using WebApi.Models.Gpio;
using WebApi.Models;

namespace WebApi.Controllers
{
    [Route("[controller]")]
    [Authorize(Policy = "Admin")]
    public class GpioController : Controller
    {
        private WebApiContext _context;
        public GpioController(WebApiContext context)
        {
            _context = context;
        }
        
        // get all controls
        [HttpGet]
        public JsonResult Get()
        {
            return Json(_context.ControlModels.ToList());
        }

        // add new control
        [HttpPost]
        public IActionResult Post([FromBody]ControlModel control)
        {
            control.ControlModelId;
            _context.ControlModels.Add(control);
            _context.SaveChanges();
            return Ok();
        }
        // update control
        [HttpPut]
        public IActionResult Put([FromBody]ControlModel control)
        {
            var controlModel = _context.ControlModels
                .SingleOrDefault(m => m.ControlModelId == control.ControlModelId);
            if(controlModel == null)
            {
                return NotFound(control.ControlModelId);
            }
            controlModel.Description = control.Description;
            controlModel.Status = control.Status;
            controlModel.Tooltip = control.Tooltip;
            controlModel.Parameters = control.Parameters;
            controlModel.Value = control.Value;
            _context.ControlModels.Update(controlModel);
            _context.SaveChanges();
            return Ok();
        }

        // delete control
        [HttpDelete]
        public IActionResult Delete(long id)
        {
            var controlModel = _context.ControlModels.SingleOrDefault(m => m.ControlModelId == id);
            if(controlModel == null)
            {
                return NotFound(id);
            }

            _context.ControlModels.Remove(controlModel);
            _context.SaveChanges();

            return Ok();
        }
    }
}