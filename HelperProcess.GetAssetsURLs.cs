using System.IO;
using System.Linq;
using System.Net.Http;
using System.Runtime.Serialization;
using System.Runtime.Serialization.Json;
using System.Threading.Tasks;

namespace HiyaCFW_Helper
{
    public partial class HelperProcess
    {
        // Internal classes for JSON parsing
        [DataContract]
        internal class Asset
        {
            [DataMember]
            internal string browser_download_url;
        }

        [DataContract]
        internal class Release
        {
            [DataMember]
            internal Asset[] assets;
        }

        private async Task<string[]> GetAssetsURLs(string repo)
        {
            Release release = new Release();

            using (HttpResponseMessage response = await client.GetAsync($"https://api.github.com/repos/{repo}/releases/latest", cancellationToken))
            {
                response.EnsureSuccessStatusCode();

                // Parse JSON
                // TODO: Do this using System.Text.Json when gets included by default in .NET
                using (MemoryStream memoryStream = new MemoryStream(await response.Content.ReadAsByteArrayAsync()))
                {
                    DataContractJsonSerializer serializer = new DataContractJsonSerializer(release.GetType());
                    release = serializer.ReadObject(memoryStream) as Release;
                }
            }

            return release.assets.Select(asset => asset.browser_download_url).ToArray();
        }
    }
}
