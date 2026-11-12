param([string]$Source, [string]$Output)
$ErrorActionPreference = 'Stop'
$sourcePath = (Resolve-Path -LiteralPath $Source).Path
$outPath = [IO.Path]::GetFullPath($Output)
New-Item -ItemType Directory -Force -Path $outPath | Out-Null
$app = New-Object -ComObject PowerPoint.Application
$app.AutomationSecurity = 3
$app.DisplayAlerts = 1
try {
    foreach ($file in Get-ChildItem -LiteralPath $sourcePath -Filter '*.ppt') {
        $deckDir = Join-Path $outPath $file.BaseName
        New-Item -ItemType Directory -Force -Path $deckDir | Out-Null
        $pres = $app.Presentations.Open($file.FullName, -1, 0, 0)
        try {
            $pres.SaveAs((Join-Path $deckDir 'source.pptx'), 24)
            $pres.SaveAs((Join-Path $deckDir 'source.pdf'), 32)
            $pres.Export((Join-Path $deckDir 'slides'), 'PNG', 1200, 900)
            [pscustomobject]@{name=$file.Name;slides=$pres.Slides.Count;width=$pres.PageSetup.SlideWidth;height=$pres.PageSetup.SlideHeight} | ConvertTo-Json | Set-Content -Encoding utf8 (Join-Path $deckDir 'metadata.json')
            Write-Output "$($file.Name): $($pres.Slides.Count) slides"
        } finally { $pres.Close() }
    }
} finally { $app.Quit() }
