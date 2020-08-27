using System;
using System.Diagnostics;
using System.IO;
using System.Security.Cryptography;
using System.Threading;
using System.Threading.Tasks;

namespace HiyaCFW_Helper
{
    public partial class HelperProcess
    {
        // Convert byte array to hex string
        // Taken from https://stackoverflow.com/questions/311165/how-do-you-convert-a-byte-array-to-a-hexadecimal-string-and-vice-versa/14333437#14333437
        private static string ByteToHexBitFiddle(byte[] bytes)
        {
            char[] c = new char[bytes.Length * 2];
            int b;
            for (int i = 0; i < bytes.Length; i++)
            {
                b = bytes[i] >> 4;
                c[i * 2] = (char)(55 + b + (((b - 10) >> 31) & -7));
                b = bytes[i] & 0xF;
                c[i * 2 + 1] = (char)(55 + b + (((b - 10) >> 31) & -7));
            }
            return new string(c);
        }

        // Run a process asynchronously
        private async Task<int> ExecAsync(Process process)
        {
            TaskCompletionSource<int> completionSource = new TaskCompletionSource<int>();

            process.Start();

            process.Exited += (object sender, EventArgs e) => completionSource.TrySetResult(process.ExitCode);

            if (process.HasExited)
            {
                return process.ExitCode;
            }

            using (CancellationTokenRegistration registration = cancellationToken.Register(() => completionSource.TrySetCanceled(cancellationToken)))
            {
                return await completionSource.Task;
            }
        }

        private async Task<string> Hash(string filename)
        {
            // Fail if file does not exist
            if (!File.Exists(filename))
            {
                throw new Exception($"File {filename} not found");
            }

            // Read the file using a 1 MiB buffer
            using (FileStream fileStream = new FileStream(filename, FileMode.Open, FileAccess.Read, FileShare.Read, 1048576, true))
            {
                using (SHA1Managed sha1 = new SHA1Managed())
                {
                    byte[] buffer = new byte[1048576];

                    while (true)
                    {
                        int read = await fileStream.ReadAsync(buffer, 0, 1048576, cancellationToken);

                        if (fileStream.Position == fileStream.Length)
                        {
                            sha1.TransformFinalBlock(buffer, 0, read);
                            break;
                        }
                        sha1.TransformBlock(buffer, 0, read, default(byte[]), default(int));
                    }

                    return ByteToHexBitFiddle(sha1.Hash);
                }
            }
        }
    }
}
