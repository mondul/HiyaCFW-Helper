using Microsoft.Win32;
using System;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Windows;
using System.Windows.Interop;

namespace HiyaCFW_Helper
{
    /// <summary>
    /// Lógica de interacción para MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        // Win32 API methods for gaining access to the WPF Window’s system ContextMenu and inserting our custom item into it
        [DllImport("user32.dll")]
        private static extern IntPtr GetSystemMenu(IntPtr hWnd, bool bRevert);

        [DllImport("user32.dll")]
        private static extern bool InsertMenu(IntPtr hMenu, Int32 wPosition, Int32 wFlags, Int32 wIDNewItem, string lpNewItem);

        //A window receives this message when the user chooses a command from the Window menu, or when the user chooses the maximize button, minimize button, restore button, or close button.
        private const Int32 WM_SYSCOMMAND = 0x112;

        //Draws a horizontal dividing line.This flag is used only in a drop-down menu, submenu, or shortcut menu.The line cannot be grayed, disabled, or highlighted.
        private const Int32 MF_SEPARATOR = 0x800;

        //Specifies that an ID is a position index into the menu and not a command ID.
        private const Int32 MF_BYPOSITION = 0x400;

        //Specifies that the menu item is a text string.
        private const Int32 MF_STRING = 0x0;

        //Menu Id for our custom menu item.
        private const Int32 _AboutMenuItemId = 1000;

        public MainWindow()
        {
            InitializeComponent();
            Loaded += MainWindow_Loaded;
        }

        private void MainWindow_Loaded(object sender, RoutedEventArgs e)
        {
            IntPtr windowhandle = new WindowInteropHelper(this).Handle;
            HwndSource hwndSource = HwndSource.FromHwnd(windowhandle);

            //Get the handle for the system menu
            IntPtr systemMenuHandle = GetSystemMenu(windowhandle, false);

            //Insert our custom menu item after Maximize
            InsertMenu(systemMenuHandle, 5, MF_BYPOSITION | MF_SEPARATOR, 0, string.Empty); //Add a menu seperator
            InsertMenu(systemMenuHandle, 6, MF_BYPOSITION, _AboutMenuItemId, "About HiyaCFW Helper"); //Add the about menu item

            hwndSource.AddHook(new HwndSourceHook(WndProc));
        }

        private IntPtr WndProc(IntPtr hwnd, int msg, IntPtr wParam, IntPtr lParam, ref bool handled)
        {
            // Check if the SystemCommand message has been executed
            if (msg == WM_SYSCOMMAND)
            {
                //check which menu item was clicked
                switch (wParam.ToInt32())
                {
                    case _AboutMenuItemId:
                        MessageBox.Show($"HiyaCFW Helper\r\nVersion {Assembly.GetExecutingAssembly().GetName().Version}\r\n\r\nhttps://github.com/mondul",
                            "About - HiyaCFW Helper", MessageBoxButton.OK, MessageBoxImage.Information);
                        handled = true;
                        break;
                }
            }

            return IntPtr.Zero;
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
            System.Windows.Forms.FolderBrowserDialog folderDialog = new System.Windows.Forms.FolderBrowserDialog
            {
                Description = "Please choose your SD card drive path or an output folder for the custom firmware files. In order to avoid boot errors please assure it is empty before continuing."
            };

            driveTxt.Text = folderDialog.ShowDialog() == System.Windows.Forms.DialogResult.OK ? folderDialog.SelectedPath : string.Empty;

            EnableStartBtn();
        }

        private void startBtn_Click(object sender, RoutedEventArgs e)
        {
            LogWindow logWindow = new LogWindow(nandTxt.Text, driveTxt.Text, twilightChk.IsChecked.GetValueOrDefault());
            logWindow.ShowDialog();
        }

        private void quitBtn_Click(object sender, RoutedEventArgs e)
        {
            this.Close();
        }
    }
}
