# Script para organizar o Desktop do Windows
# Execute como: clique direito > "Executar com PowerShell"

$desktop = [Environment]::GetFolderPath("Desktop")

$pastas = @{
    "Imagens"    = @(".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico", ".tiff", ".raw")
    "Videos"     = @(".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v")
    "Musicas"    = @(".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a")
    "Documentos" = @(".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".odt", ".ods")
    "Compactados" = @(".zip", ".rar", ".7z", ".tar", ".gz", ".bz2")
    "Programas"  = @(".exe", ".msi", ".bat", ".cmd", ".ps1", ".sh")
    "Codigo"     = @(".py", ".js", ".ts", ".html", ".css", ".java", ".cs", ".cpp", ".c", ".json", ".xml", ".yaml", ".yml")
    "Outros"     = @()
}

$movidos = 0
$ignorados = 0

Get-ChildItem -Path $desktop -File | ForEach-Object {
    $arquivo = $_
    $extensao = $arquivo.Extension.ToLower()
    $destino = $null

    foreach ($pasta in $pastas.Keys) {
        if ($pastas[$pasta] -contains $extensao) {
            $destino = Join-Path $desktop $pasta
            break
        }
    }

    if (-not $destino) {
        $destino = Join-Path $desktop "Outros"
    }

    if (-not (Test-Path $destino)) {
        New-Item -ItemType Directory -Path $destino | Out-Null
    }

    $novocaminho = Join-Path $destino $arquivo.Name

    if (Test-Path $novocaminho) {
        $base = [System.IO.Path]::GetFileNameWithoutExtension($arquivo.Name)
        $ext  = $arquivo.Extension
        $i = 1
        do {
            $novoNome = "${base}_${i}${ext}"
            $novocaminho = Join-Path $destino $novoNome
            $i++
        } while (Test-Path $novocaminho)
    }

    Move-Item -Path $arquivo.FullName -Destination $novocaminho
    Write-Host "Movido: $($arquivo.Name) -> $destino"
    $movidos++
}

Write-Host ""
Write-Host "Concluido! $movidos arquivo(s) organizado(s)."
Write-Host "Pressione qualquer tecla para fechar..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
