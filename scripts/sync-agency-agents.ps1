#Requires -Version 5.1
<#
  从 GitHub 同步 agency-agents-zh 官方智能体定义到本仓库 .cursor/agents/
  用法：在仓库根目录执行  .\scripts\sync-agency-agents.ps1
#>
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Vendor = Join-Path $Root "third_party\agency-agents-zh"
$Agents = Join-Path $Root ".cursor\agents"
$Repo = "https://github.com/jnMetaCode/agency-agents-zh.git"

New-Item -ItemType Directory -Force -Path $Agents | Out-Null
New-Item -ItemType Directory -Force -Path (Split-Path $Vendor) | Out-Null

if (-not (Test-Path (Join-Path $Vendor ".git"))) {
    git clone --depth 1 $Repo $Vendor
} else {
    Push-Location $Vendor
    git pull --ff-only
    Pop-Location
}

$Pairs = @(
    @{ Src = "specialized\prompt-engineer.md"; Dst = "prompt-engineer.md" },
    @{ Src = "project-management\project-manager-senior.md"; Dst = "project-manager-senior.md" },
    @{ Src = "specialized\agents-orchestrator.md"; Dst = "agents-orchestrator.md" },
    @{ Src = "engineering\engineering-data-engineer.md"; Dst = "engineering-data-engineer.md" },
    @{ Src = "marketing\marketing-daily-news-briefing.md"; Dst = "marketing-daily-news-briefing.md" },
    @{ Src = "finance\finance-investment-researcher.md"; Dst = "finance-investment-researcher.md" },
    @{ Src = "testing\testing-reality-checker.md"; Dst = "testing-reality-checker.md" }
)

foreach ($p in $Pairs) {
    $from = Join-Path $Vendor $p.Src
    $to = Join-Path $Agents $p.Dst
    if (-not (Test-Path $from)) { throw "Missing upstream file: $($p.Src)" }
    Copy-Item -LiteralPath $from -Destination $to -Force
    Write-Host "Copied $($p.Src) -> .cursor/agents/$($p.Dst)"
}

$rev = (git -C $Vendor rev-parse HEAD)
$revFile = Join-Path $Root "AGENCY_AGENTS_REVISION.txt"
Set-Content -Path $revFile -Value $rev -Encoding utf8
Write-Host "Recorded upstream revision to AGENCY_AGENTS_REVISION.txt"
