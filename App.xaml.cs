using Microsoft.Win32;
using System;
using System.IO;
using System.Windows;

namespace HiyaCFW_Helper
{
    /// <summary>
    /// Lógica de interacción para App.xaml
    /// </summary>
    public partial class App : Application
    {
        public static string _7z;

        private void Application_Startup(object sender, StartupEventArgs e)
        {
            // Search for 7-Zip in the 64-bit registry
            RegistryKey HKLM = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64);
            RegistryKey _7zKey = HKLM.OpenSubKey(@"SOFTWARE\7-Zip");

            if (_7zKey == null)
            {
                HKLM.Close();

                // If not found, search for 7-Zip in the 32-bit registry
                HKLM = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry32);
                _7zKey = HKLM.OpenSubKey(@"SOFTWARE\7-Zip");

                if (_7zKey == null)
                {
                    HKLM.Close();
                    MessageBox.Show("7-Zip not found. Please download it from https://www.7-zip.org/download.html", "Error - HiyaCFW Helper", MessageBoxButton.OK, MessageBoxImage.Error);
                    Environment.Exit(1);
                }

                else
                {
                    _7z = _7zKey.GetValue("Path").ToString();
                    _7zKey.Close();
                    HKLM.Close();
                }
            }

            else
            {
                _7z = _7zKey.GetValue("Path").ToString();
                _7zKey.Close();
                HKLM.Close();
            }

            _7z = Path.Combine(_7z, "7z.exe");

            new MainWindow().Show();
        }
    }
}
