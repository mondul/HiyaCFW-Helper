using System;
using System.ComponentModel;
using System.IO;
using System.Threading;
using System.Windows;

namespace HiyaCFW_Helper
{
    /// <summary>
    /// Lógica de interacción para LogWindow.xaml
    /// </summary>
    public partial class LogWindow : Window
    {
        private readonly string nandFile;
        private readonly string outputFolder;
        private readonly bool installTWiLight;

        private bool done;
        private readonly CancellationTokenSource cancellationTokenSource;

        public LogWindow(string nandFile, string outputFolder, bool installTWiLight)
        {
            this.nandFile = nandFile;
            this.outputFolder = outputFolder;
            this.installTWiLight = installTWiLight;

            done = false;
            cancellationTokenSource = new CancellationTokenSource();
            InitializeComponent();
            this.Owner = App.Current.MainWindow;
            // Add event after the window content is rendered
            this.ContentRendered += LogWindow_ContentRendered;
        }

        private async void LogWindow_ContentRendered(object sender, EventArgs e)
        {
            // Unset the event to avoid refiring
            this.ContentRendered -= LogWindow_ContentRendered;

            // Create and start the helper process
            HelperProcess helper = new HelperProcess(
                nandFile, outputFolder, installTWiLight,
                new Progress<string>(s => logTxt.AppendText(s + "\r\n")),
                new Progress<string>(s => statusTxt.Text = s),
                cancellationTokenSource.Token
            );

            try
            {
                // We'll use this folder for all downloaded and extracted files
                Directory.CreateDirectory("tmp");
                await helper.Start();
            }

            catch (OperationCanceledException)
            {
                MessageBox.Show("Helper process interrupted", "Warning - HiyaCFW Helper", MessageBoxButton.OK, MessageBoxImage.Warning);
            }

            catch (Exception ex)
            {
                logTxt.AppendText("--\r\nUnexpected error: " + ex.Message);
                statusTxt.Text = "Unexpected error!";
            }

            finally
            {
                cancellationTokenSource.Dispose();
                done = true;
            }
        }

        // Warn on close if the helper process is running
        protected override void OnClosing(CancelEventArgs e)
        {
            if (done)
            {
                return;
            }

            if (MessageBox.Show("Are you sure you want to interrupt the process?", "Interrupt - HiyaCFW Helper",
                MessageBoxButton.YesNo, MessageBoxImage.Question) == MessageBoxResult.No)
            {
                e.Cancel = true;
                return;
            }

            if (cancellationTokenSource != null)
            {
                cancellationTokenSource.Cancel();
            }
        }
    }
}
