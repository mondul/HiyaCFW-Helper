using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
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

        // Calculate the SHA1 of a file
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

        // Convert a byte array to int
        private static int Unpack(byte[] buf)
        {
            if (BitConverter.IsLittleEndian)
            {
                Array.Reverse(buf);
            }
            return BitConverter.ToInt32(buf, 0);
        }

        // IPS patch header: PATCH
        private static readonly byte[] patchHeader = new byte[] { 0x50, 0x41, 0x54, 0x43, 0x48 };

        // Apply an IPS patch on a file
        private async Task IPSPatch(string filename, string patchFilename)
        {
            if (!File.Exists(filename))
            {
                throw new Exception("File to patch not found");
            }
            if (!File.Exists(patchFilename))
            {
                throw new Exception("Patch file not found");
            }

            // Read the patch file
            using (FileStream patchFileStream = new FileStream(patchFilename, FileMode.Open, FileAccess.Read, FileShare.Read, 5, true))
            {
                // Check patch header
                byte[] buf = new byte[5];
                await patchFileStream.ReadAsync(buf, 0, 5, cancellationToken);
                if (!patchHeader.SequenceEqual(buf))
                {
                    throw new Exception("Invalid IPS");
                }

                // Reset buffer size
                buf = new byte[4];
                // Data buffer
                byte[] data = new byte[65535];
                // 3-byte offset
                int offset;
                // 2-byte size
                int size;
                // EOF footer position
                long eofPos = patchFileStream.Length - 3;

                // Read first record
                buf[0] = 0;
                await patchFileStream.ReadAsync(buf, 1, 3, cancellationToken);

                // Open the file to patch for writing
                using (FileStream fileStream = new FileStream(filename, FileMode.Open, FileAccess.Write, FileShare.None, 65535, true))
                {
                    while (patchFileStream.Position < eofPos)
                    {
                        // Unpack 3-byte pointer
                        offset = Unpack(buf);
                        // Read size of data chunk
                        buf[0] = 0; buf[1] = 0;
                        await patchFileStream.ReadAsync(buf, 2, 2, cancellationToken);
                        // Unpack 2-byte size
                        size = Unpack(buf);

                        // Check for RLE
                        if (size == 0)
                        {
                            // Read RLE size
                            buf[0] = 0; buf[1] = 0;
                            await patchFileStream.ReadAsync(buf, 2, 2, cancellationToken);
                            // Unpack 2-byte RLE size
                            size = Unpack(buf);

                            // Read one byte
                            await patchFileStream.ReadAsync(data, 0, 1, cancellationToken);
                            // Fill the data buffer to the found size
                            for (int i = 1; i < size; i++)
                            {
                                data[i] = data[0];
                            }
                        }
                        else
                        {
                            await patchFileStream.ReadAsync(data, 0, size, cancellationToken);
                        }

                        // Write to file
                        fileStream.Seek(offset, SeekOrigin.Begin);
                        await fileStream.WriteAsync(data, 0, size, cancellationToken);

                        // Read next record
                        buf[0] = 0;
                        await patchFileStream.ReadAsync(buf, 1, 3, cancellationToken);
                    }

                    // Check if file needs to be truncated
                    if (patchFileStream.Position == eofPos)
                    {
                        // Read truncate offset
                        buf[0] = 0;
                        await patchFileStream.ReadAsync(buf, 1, 3, cancellationToken);
                        // Unpack 3-byte pointer
                        offset = Unpack(buf);
                        // Truncate file
                        fileStream.SetLength(offset);
                    }
                }
            }
        }
    }
}
