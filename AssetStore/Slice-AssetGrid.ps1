<#
.SYNOPSIS
    Splits a 2x2 asset sheet (1024x1024) into 4 individual 512x512 PNG icons.
.EXAMPLE
    .\Slice-AssetGrid.ps1 -Source "grid_animals.jpg" -TL "item_animal_pig" -TR "item_animal_horse" -BL "item_animal_duck" -BR "item_tools_tractor"
#>
param(
    [Parameter(Mandatory=$true)]
    [string]$SourcePath,

    [Parameter(Mandatory=$true)]
    [string]$TL, # Top-Left item name

    [Parameter(Mandatory=$true)]
    [string]$TR, # Top-Right item name

    [Parameter(Mandatory=$true)]
    [string]$BL, # Bottom-Left item name

    [Parameter(Mandatory=$true)]
    [string]$BR, # Bottom-Right item name

    [string]$OutputDir = "C:\Users\Sergv\orca\workspaces\VFX\wreckfish\AssetStore\Item_Previews"
)

Add-Type -AssemblyName System.Drawing

if (!(Test-Path $SourcePath)) {
    Write-Error "Source file not found: $SourcePath"
    exit 1
}

if (!(Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

$src = [System.Drawing.Bitmap]::FromFile($SourcePath)
$halfW = [int]($src.Width / 2)
$halfH = [int]($src.Height / 2)

$quadrants = @(
    @{ Name = $TL; Rect = [System.Drawing.Rectangle]::new(0, 0, $halfW, $halfH) },
    @{ Name = $TR; Rect = [System.Drawing.Rectangle]::new($halfW, 0, $halfW, $halfH) },
    @{ Name = $BL; Rect = [System.Drawing.Rectangle]::new(0, $halfH, $halfW, $halfH) },
    @{ Name = $BR; Rect = [System.Drawing.Rectangle]::new($halfW, $halfH, $halfW, $halfH) }
)

foreach ($q in $quadrants) {
    if ([string]::IsNullOrWhiteSpace($q.Name)) { continue }
    $cropped = $src.Clone($q.Rect, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $fileName = if ($q.Name.EndsWith(".png")) { $q.Name } else { "$($q.Name).png" }
    $outPath = Join-Path $OutputDir $fileName
    $cropped.Save($outPath, [System.Drawing.Imaging.ImageFormat]::Png)
    $cropped.Dispose()
    Write-Host "Saved: $outPath ($halfW x $halfH)"
}

$src.Dispose()
Write-Host "Grid slicing completed successfully!"
