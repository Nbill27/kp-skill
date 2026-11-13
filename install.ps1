<#
.SYNOPSIS
    Install the Bina Insani KP skill into an agent skills directory.

.DESCRIPTION
    Copies skills/kerja-praktek-bina-insani into the skills directory of one
    agent, or into all of them with -All. The skill folder is self-contained,
    so a plain recursive copy is the whole install.

    Run this script from the repository root.

.PARAMETER Claude
    Claude Code, %USERPROFILE%\.claude\skills

.PARAMETER OpenCode
    OpenCode, %XDG_CONFIG_HOME% or %USERPROFILE%\.config\opencode\skills

.PARAMETER Codex
    Codex, %USERPROFILE%\.agents\skills

.PARAMETER Hermes
    Hermes, %USERPROFILE%\.hermes\skills (default)

.PARAMETER CodeBuddy
    CodeBuddy, %USERPROFILE%\.codebuddy\skills

.PARAMETER All
    Install into every agent above.

.PARAMETER Uninstall
    Remove the installed skill instead of copying it.

.PARAMETER DryRun
    Print what would happen without touching the filesystem.

.PARAMETER Help
    Show this message.

.EXAMPLE
    .\install.ps1 -Claude

.EXAMPLE
    .\install.ps1 -All -DryRun
#>
[CmdletBinding()]
param(
    [switch]$Claude,
    [switch]$OpenCode,
    [switch]$Codex,
    [switch]$Hermes,
    [switch]$CodeBuddy,
    [switch]$All,
    [switch]$Uninstall,
    [switch]$DryRun,
    [switch]$Help
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$SkillName = 'kerja-praktek-bina-insani'
$Source = Join-Path 'skills' $SkillName

function Show-Usage {
    Get-Help $PSCommandPath -Detailed
}

function Get-Targets {
    $home_dir = $env:USERPROFILE
    $config_root = if ($env:XDG_CONFIG_HOME) { $env:XDG_CONFIG_HOME } else { Join-Path $home_dir '.config' }

    $table = [ordered]@{
        Claude    = Join-Path $home_dir '.claude\skills'
        OpenCode  = Join-Path $config_root 'opencode\skills'
        Codex     = Join-Path $home_dir '.agents\skills'
        Hermes    = Join-Path $home_dir '.hermes\skills'
        CodeBuddy = Join-Path $home_dir '.codebuddy\skills'
    }

    $selected = @()
    if ($Claude) { $selected += 'Claude' }
    if ($OpenCode) { $selected += 'OpenCode' }
    if ($Codex) { $selected += 'Codex' }
    if ($Hermes) { $selected += 'Hermes' }
    if ($CodeBuddy) { $selected += 'CodeBuddy' }

    if ($All) { return $table }

    if ($selected.Count -eq 0) {
        return [ordered]@{ Hermes = $table.Hermes }
    }
    if ($selected.Count -gt 1) {
        throw "Pick one agent, or use -All. Got: $($selected -join ', ')"
    }

    $picked = [ordered]@{}
    $picked[$selected[0]] = $table[$selected[0]]
    return $picked
}

function Install-One {
    param([string]$Agent, [string]$Root)

    $destination = Join-Path $Root $SkillName

    if ($Uninstall) {
        if (Test-Path -LiteralPath $destination) {
            if ($DryRun) {
                Write-Host "would remove  $destination"
            }
            else {
                Remove-Item -LiteralPath $destination -Recurse -Force
                Write-Host "removed       $destination"
            }
        }
        else {
            Write-Host "not installed $destination"
        }
        return
    }

    if ($DryRun) {
        Write-Host "would install $Source -> $destination"
        return
    }

    New-Item -ItemType Directory -Force -Path $Root | Out-Null
    # Remove first so a reinstall cannot leave a file that no longer ships.
    if (Test-Path -LiteralPath $destination) {
        Remove-Item -LiteralPath $destination -Recurse -Force
    }
    Copy-Item -LiteralPath $Source -Destination $Root -Recurse -Force
    Write-Host "installed     $destination ($Agent)"
}

function Show-VerifyHint {
    param([string[]]$Agents)

    $hints = @{
        Claude    = 'run /skills inside claude'
        OpenCode  = 'mention @kerja-praktek-bina-insani in a prompt'
        Codex     = 'run /skills in the Codex CLI'
        Hermes    = 'hermes skills list'
        CodeBuddy = 'check the CodeBuddy skills list'
    }

    Write-Host ''
    Write-Host 'Verify:'
    foreach ($agent in $Agents) {
        Write-Host "  $agent - $($hints[$agent])"
    }
}

if ($Help) {
    Show-Usage
    exit 0
}

if (-not (Test-Path -LiteralPath $Source -PathType Container)) {
    Write-Error "Run this script from the repo root: $Source not found."
    exit 1
}

$targets = Get-Targets
foreach ($agent in $targets.Keys) {
    Install-One -Agent $agent -Root $targets[$agent]
}

if (-not $Uninstall -and -not $DryRun) {
    Show-VerifyHint -Agents @($targets.Keys)
}
elseif ($DryRun) {
    Write-Host ''
    Write-Host 'Dry run: nothing was written.'
}
