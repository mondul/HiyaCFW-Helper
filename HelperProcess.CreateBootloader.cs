using System;
using System.Diagnostics;
using System.IO;
using System.Threading.Tasks;

namespace HiyaCFW_Helper
{
    public partial class HelperProcess
    {
        private async Task ExtractBIOS()
        {
            log.Report("  - Extracting ARM7/ARM9 BIOS from NAND...");

            using (Process process = new Process()
            {
                StartInfo = new ProcessStartInfo
                {
                    FileName = Path.Combine("tmp", "for PC", "twltool.exe"),
                    Arguments = $"boot2 --in \"{nandFile}\"",
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

            if (!File.Exists("arm7.bin") || !File.Exists("arm9.bin"))
            {
                throw new Exception("Needed files were not extracted, cannot continue");
            }

            log.Report("    OK");
            log.Report($"    arm7.bin SHA1: {await Hash("arm7.bin")}");
            log.Report($"    arm9.bin SHA1: {await Hash("arm9.bin")}");
        }

        private async Task PatchBIOS()
        {
            log.Report("  - Patching ARM7/ARM9 BIOS...");
            await IPSPatch("arm7.bin", Path.Combine("tmp", "for PC", "bootloader files", "bootloader arm7 patch.ips"));
            await IPSPatch("arm9.bin", Path.Combine("tmp", "for PC", "bootloader files", "bootloader arm9 patch.ips"));

            log.Report("    OK");
            log.Report($"    Patched arm7.bin SHA1: {await Hash("arm7.bin")}");
            log.Report($"    Patched arm9.bin SHA1: {await Hash("arm9.bin")}");
        }

        private async Task CreateBootloader()
        {
            log.Report("• Creating bootloader...");
            await ExtractBIOS();
            await PatchBIOS();
        }
    }
}
