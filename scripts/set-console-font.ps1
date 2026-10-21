# Larger raster/TrueType font so 1080p gdigrab of conhost stays readable.
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
[StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
public struct COORD { public short X; public short Y; }
[StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
public struct CONSOLE_FONT_INFOEX {
  public uint cbSize;
  public uint nFont;
  public COORD dwFontSize;
  public int FontFamily;
  public int FontWeight;
  [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)]
  public string FaceName;
}
public class ConFont {
  [DllImport("kernel32.dll", SetLastError = true)]
  public static extern IntPtr GetStdHandle(int nStdHandle);
  [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
  public static extern bool SetCurrentConsoleFontEx(IntPtr hConsoleOutput, bool bMaximumWindow, ref CONSOLE_FONT_INFOEX lpConsoleCurrentFontEx);
  public static void Apply(short size) {
    var info = new CONSOLE_FONT_INFOEX();
    info.cbSize = (uint)Marshal.SizeOf(typeof(CONSOLE_FONT_INFOEX));
    info.FaceName = "Consolas";
    info.dwFontSize = new COORD { X = 0, Y = size };
    info.FontWeight = 400;
    info.FontFamily = 54;
    SetCurrentConsoleFontEx(GetStdHandle(-11), false, ref info);
  }
}
"@
try { [ConFont]::Apply(24) } catch {}
