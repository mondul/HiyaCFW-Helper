using System;
using System.Threading;
using System.Threading.Tasks;

namespace HiyaCFW_Helper
{
    public partial class HelperProcess
    {
        private readonly string nandFile;
        private readonly string outputFolder;
        private readonly bool installTWiLight;

        private readonly IProgress<string> log;
        private readonly IProgress<string> status;
        private readonly CancellationToken cancellationToken;

        public HelperProcess(string nandFile, string outputFolder, bool installTWiLight, Progress<string> log, Progress<string> status, CancellationToken cancellationToken)
        {
            this.nandFile = nandFile;
            this.outputFolder = outputFolder;
            this.installTWiLight = installTWiLight;

            this.log = log;
            this.status = status;
            this.cancellationToken = cancellationToken;
        }

        private void LogError(string txt)
        {
            log.Report(txt);
            status.Report("Error!");
        }

        public async Task Start()
        {
            // Check NAND file
            if (await CheckNAND())
            {
                LogError("  ERROR: No$GBA footer not found");
                return;
            }

            status.Report("Done!");
        }
    }
}
