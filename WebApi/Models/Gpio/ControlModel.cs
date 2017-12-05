namespace WebApi.Models.Gpio
{
    public class ControlModel
    {
        public long ControlModelId { get; set; }
        public string Description { get; set; }
        public string Status { get; set; }
        public string Tooltip { get; set; }
        public string Parameters {get; set; }
        public bool Value { get; set; }
    }
}