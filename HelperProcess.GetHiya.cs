using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Net;
using System.Threading;
using System.Threading.Tasks;

namespace HiyaCFW_Helper
{
    public partial class HelperProcess
    {
        private async Task GetHiya()
        {
            log.Report("• Getting latest HiyaCFW release...\r\n  - Getting archive URL from GitHub API...");

            string[] urls = await GetAssetsURLs("RocketRobz/hiyaCFW");

            log.Report("  - Downloading archive...");

            Uri uri = new Uri(urls.FirstOrDefault());
            string archive = Path.Combine("tmp", uri.Segments.Last());

            using (WebClient client = new WebClient())
            {
                using (CancellationTokenRegistration registration = cancellationToken.Register(() => client.CancelAsync()))
                {
                    await client.DownloadFileTaskAsync(uri, archive);
                }
            }

            log.Report("  - Extracting archive...");

            using (Process process = new Process()
            {
                StartInfo = new ProcessStartInfo
                {
                    FileName = App._7z,
                    Arguments = $"x -bso0 -bsp0 -y -otmp {archive} \"for PC\" \"for SDNAND SD card\"",
                    CreateNoWindow = true,
                    UseShellExecute = false,
                    RedirectStandardError = true
                },
                EnableRaisingEvents = true
            })
            {
                int exitCode;

                try
                {
                    exitCode = await ExecAsync(process);
                }

                catch (OperationCanceledException)
                {
                    process.Kill();
                    throw;
                }

                if (exitCode != 0)
                {
                    throw new Exception(await process.StandardError.ReadToEndAsync());
                }
            }

            if (!Directory.Exists(Path.Combine("tmp", "for PC")) || !Directory.Exists(Path.Combine("tmp", "for SDNAND SD card")))
            {
                throw new Exception("Needed folders were not extracted, cannot continue");
            }

            // Delete archive as is no longer needed
            File.Delete(archive);

            log.Report("    OK\r\n");
        }
    }
}
