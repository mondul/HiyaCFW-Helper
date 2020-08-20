using System;
using System.Windows;
using System.Windows.Forms;
using OpenFileDialog = Microsoft.Win32.OpenFileDialog;

namespace HiyaCFW_Helper
{
    /// <summary>
    /// Lógica de interacción para MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();
        }


        private void EnableStartBtn()
        {
            startBtn.IsEnabled = (nandTxt.Text.Length > 0) & (driveTxt.Text.Length > 0);
        }

        private void browseNandBtn_Click(object sender, RoutedEventArgs e)
        {
            OpenFileDialog fileDialog = new OpenFileDialog
            {
                Title = "Please choose your DSi NAND file",
                Filter = "DSi NAND dump (*.bin)|*.bin|No$gba MMC (*.mmc)|*.mmc|All files (*.*)|*.*"
            };

            nandTxt.Text = fileDialog.ShowDialog() == true ? fileDialog.FileName : string.Empty;

            EnableStartBtn();
        }

        private void browseDriveBtn_Click(object sender, RoutedEventArgs e)
        {
            FolderBrowserDialog folderDialog = new FolderBrowserDialog
            {
                Description = "Please choose your SD card drive path or an output folder for the custom firmware files:"
            };

            driveTxt.Text = folderDialog.ShowDialog() == System.Windows.Forms.DialogResult.OK ? folderDialog.SelectedPath : string.Empty;

            EnableStartBtn();
        }

        private void startBtn_Click(object sender, RoutedEventArgs e)
        {

        }

        private void quitBtn_Click(object sender, RoutedEventArgs e)
        {
            Environment.Exit(0);
        }
    }
}
