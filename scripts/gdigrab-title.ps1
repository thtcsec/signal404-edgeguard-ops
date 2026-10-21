# ffmpeg gdigrab by window title. Uses splat so titles with spaces stay intact.
param(
    [Parameter(Mandatory = $true)][string]$Title,
    [Parameter(Mandatory = $true)][string]$OutMp4,
    [int]$Seconds = 90
)
$ErrorActionPreference = "Stop"
$ffArgs = @(
    "-y", "-f", "gdigrab", "-framerate", "30", "-draw_mouse", "0",
    "-i", "title=$Title",
    "-t", "$Seconds",
    "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=30",
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", "20",
    "-movflags", "+frag_keyframe+empty_moov+default_base_moof",
    $OutMp4
)
Write-Host "GDIGRAB title=$Title -> $OutMp4 ($Seconds s)"
& ffmpeg @ffArgs
if ($LASTEXITCODE -ne 0 -or -not (Test-Path $OutMp4) -or ((Get-Item $OutMp4).Length -lt 40000)) {
    Write-Host "GDIGRAB_FAILED exit=$LASTEXITCODE size=$((Get-Item $OutMp4 -ErrorAction SilentlyContinue).Length)"
    exit 4
}
Write-Host "GDIGRAB_OK" $OutMp4 ((Get-Item $OutMp4).Length)
exit 0
