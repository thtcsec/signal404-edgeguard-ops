# Capture a classic conhost.exe console by window title (GDI).
# Windows Terminal / powershell.exe default host often records as a black frame.
param(
    [Parameter(Mandatory = $true)][string]$Title,
    [Parameter(Mandatory = $true)][string]$ScriptPath,
    [Parameter(Mandatory = $true)][string]$OutMp4,
    [int]$Seconds = 22,
    [int]$WarmupSeconds = 4,
    [switch]$KeepAlive
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path -LiteralPath $ScriptPath)) { throw "Missing $ScriptPath" }

$conhost = Join-Path $env:SystemRoot "System32\conhost.exe"
if (-not (Test-Path $conhost)) { throw "conhost.exe not found" }

$arg = @(
    "--headless=false",
    "powershell.exe",
    "-NoLogo", "-NoProfile", "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-File", $ScriptPath
)
# Some Windows builds ignore unknown --headless; also try without if launch fails.
$proc = Start-Process -FilePath $conhost -ArgumentList @(
    "powershell.exe", "-NoLogo", "-NoProfile", "-NoExit",
    "-ExecutionPolicy", "Bypass", "-File", "`"$ScriptPath`""
) -PassThru
Start-Sleep -Seconds $WarmupSeconds

Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
using System.Text;
public class WinFg {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc lpEnumFunc, IntPtr lParam);
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);
  public delegate bool EnumProc(IntPtr hWnd, IntPtr lParam);
  public static IntPtr FindTitle(string needle) {
    IntPtr found = IntPtr.Zero;
    EnumWindows((h, l) => {
      var sb = new StringBuilder(512);
      GetWindowText(h, sb, sb.Capacity);
      if (sb.ToString().IndexOf(needle, StringComparison.OrdinalIgnoreCase) >= 0) {
        found = h; return false;
      }
      return true;
    }, IntPtr.Zero);
    return found;
  }
}
"@

$hwnd = [WinFg]::FindTitle($Title)
if ($hwnd -eq [IntPtr]::Zero -and $proc.MainWindowHandle -ne [IntPtr]::Zero) {
    $hwnd = $proc.MainWindowHandle
}
if ($hwnd -ne [IntPtr]::Zero) {
    [WinFg]::ShowWindow($hwnd, 3) | Out-Null  # SW_MAXIMIZE
    [WinFg]::SetForegroundWindow($hwnd) | Out-Null
}
Start-Sleep -Seconds 1

$ffArgs = @(
    "-y", "-f", "gdigrab", "-framerate", "30",
    "-draw_mouse", "0",
    "-i", "title=$Title",
    "-t", "$Seconds",
    "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=30",
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", "20",
    "-movflags", "+frag_keyframe+empty_moov+default_base_moof",
    $OutMp4
)
$meta = @{
    title = $Title
    script = $ScriptPath
    output = $OutMp4
    seconds = $Seconds
    warmup_seconds = $WarmupSeconds
    keep_alive = [bool]$KeepAlive
    started_utc = (Get-Date).ToUniversalTime().ToString("o")
}
$metaPath = "$OutMp4.meta.json"
($meta | ConvertTo-Json) | Set-Content -Path $metaPath -Encoding utf8

Write-Host "CONHOST_REC title=$Title -> $OutMp4 ($Seconds s) keepAlive=$KeepAlive"
& ffmpeg @ffArgs
$ffExit = $LASTEXITCODE
$meta.ended_utc = (Get-Date).ToUniversalTime().ToString("o")
$meta.ffmpeg_exit = $ffExit
if (Test-Path $OutMp4) { $meta.size_bytes = (Get-Item $OutMp4).Length }
($meta | ConvertTo-Json) | Set-Content -Path $metaPath -Encoding utf8

if (-not $KeepAlive) {
    Get-CimInstance Win32_Process | Where-Object {
        $_.ParentProcessId -eq $proc.Id -or $_.ProcessId -eq $proc.Id
    } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
}

if ($ffExit -ne 0 -or -not (Test-Path $OutMp4) -or ((Get-Item $OutMp4).Length -lt 40000)) {
    Write-Host "CONHOST_REC_FAILED size=$((Get-Item $OutMp4 -ErrorAction SilentlyContinue).Length) exit=$ffExit"
    exit 4
}
Write-Host "CONHOST_REC_OK" $OutMp4 ((Get-Item $OutMp4).Length)
exit 0
