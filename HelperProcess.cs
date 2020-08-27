using System;
using System.Net.Http;
using System.Threading;
using System.Threading.Tasks;

namespace HiyaCFW_Helper
{
    public partial class HelperProcess
    {
        private static readonly HttpClient client = new HttpClient();

        private readonly string nandFile;
        private readonly string outputFolder;
        private readonly bool installTWiLight;

        private readonly IProgress<string> log;
        private readonly IProgress<string> status;
        private readonly CancellationToken cancellationToken;

        public HelperProcess(string nandFile, string outputFolder, bool installTWiLight, Progress<string> log, Progress<string> status, CancellationToken cancellationToken)
        {
            // GitHub API requires an user agent to be sent
            client.DefaultRequestHeaders.UserAgent.ParseAdd("curl/4.0");

            this.nandFile = nandFile;
            this.outputFolder = outputFolder;
            this.installTWiLight = installTWiLight;

            this.log = log;
            this.status = status;
            this.cancellationToken = cancellationToken;
        }

        public async Task Start()
        {
            // Check NAND file
            await CheckNAND();
            // Download and extract HiyaCFW
            await GetHiya();
            // Extract and patch BIOS, and create bootloader
            await CreateBootloader();

            status.Report("Done!");
        }
    }
}
