# ============================================================
#  Script: Limpeza e Deteccao de Duplicatas
#  - Move arquivos antigos (90+ dias sem acesso) para revisao
#  - Move arquivos duplicados para revisao
#  - NAO EXCLUI NADA - voce decide depois
# ============================================================

$pastasVerificar = @(
    [Environment]::GetFolderPath("UserProfile") + "\Downloads",
    [Environment]::GetFolderPath("Desktop"),
    [Environment]::GetFolderPath("MyDocuments")
)

$pastaRevisao   = [Environment]::GetFolderPath("UserProfile") + "\REVISAO_PARA_EXCLUIR"
$pastaAntigos   = Join-Path $pastaRevisao "Arquivos_Antigos"
$pastaDuplicatas = Join-Path $pastaRevisao "Duplicatas"
$diasAntigo     = 90
$relatorio      = Join-Path $pastaRevisao "relatorio.txt"

# Cria pastas de destino
foreach ($p in @($pastaRevisao, $pastaAntigos, $pastaDuplicatas)) {
    if (-not (Test-Path $p)) { New-Item -ItemType Directory -Path $p | Out-Null }
}

$linhasRelatorio = @()
$linhasRelatorio += "============================================"
$linhasRelatorio += " RELATORIO DE LIMPEZA - $(Get-Date -Format 'dd/MM/yyyy HH:mm')"
$linhasRelatorio += "============================================"

# ---- Funcao: mover sem sobrescrever ----
function Mover-Arquivo($origem, $pastaDestino) {
    $nome = Split-Path $origem -Leaf
    $destino = Join-Path $pastaDestino $nome
    if (Test-Path $destino) {
        $base = [System.IO.Path]::GetFileNameWithoutExtension($nome)
        $ext  = [System.IO.Path]::GetExtension($nome)
        $i = 1
        do { $destino = Join-Path $pastaDestino "${base}_copia${i}${ext}"; $i++ } while (Test-Path $destino)
    }
    Move-Item -Path $origem -Destination $destino -Force
    return $destino
}

# ============================================================
# ETAPA 1 — Arquivos antigos (90+ dias sem acesso)
# ============================================================
Write-Host ""
Write-Host "=== ETAPA 1: Buscando arquivos antigos (90+ dias) ===" -ForegroundColor Cyan
$linhasRelatorio += ""; $linhasRelatorio += "--- ARQUIVOS ANTIGOS (nao acessados ha $diasAntigo+ dias) ---"

$totalAntigos = 0
$limite = (Get-Date).AddDays(-$diasAntigo)

foreach ($pasta in $pastasVerificar) {
    if (-not (Test-Path $pasta)) { continue }
    $nomePasta = Split-Path $pasta -Leaf

    Get-ChildItem -Path $pasta -File -Recurse -ErrorAction SilentlyContinue | Where-Object {
        $_.LastAccessTime -lt $limite
    } | ForEach-Object {
        $destSubpasta = Join-Path $pastaAntigos $nomePasta
        if (-not (Test-Path $destSubpasta)) { New-Item -ItemType Directory -Path $destSubpasta | Out-Null }
        $novo = Mover-Arquivo $_.FullName $destSubpasta
        $msg = "[ANTIGO] $($_.FullName) -> $novo"
        Write-Host $msg -ForegroundColor Yellow
        $linhasRelatorio += $msg
        $totalAntigos++
    }
}

Write-Host "Total de arquivos antigos movidos: $totalAntigos" -ForegroundColor Green

# ============================================================
# ETAPA 2 — Arquivos duplicados (mesmo conteudo/hash)
# ============================================================
Write-Host ""
Write-Host "=== ETAPA 2: Buscando arquivos duplicados ===" -ForegroundColor Cyan
$linhasRelatorio += ""; $linhasRelatorio += "--- ARQUIVOS DUPLICADOS ---"

$hashMap = @{}
$totalDuplicatas = 0

foreach ($pasta in $pastasVerificar) {
    if (-not (Test-Path $pasta)) { continue }
    Get-ChildItem -Path $pasta -File -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
        try {
            $hash = (Get-FileHash $_.FullName -Algorithm MD5).Hash
            if ($hashMap.ContainsKey($hash)) {
                $hashMap[$hash] += , $_.FullName
            } else {
                $hashMap[$hash] = @($_.FullName)
            }
        } catch {}
    }
}

foreach ($hash in $hashMap.Keys) {
    $arquivos = $hashMap[$hash]
    if ($arquivos.Count -lt 2) { continue }

    # Mantem o mais recente, move os outros
    $ordenados = $arquivos | Sort-Object { (Get-Item $_ -ErrorAction SilentlyContinue).LastWriteTime } -Descending
    $original  = $ordenados[0]
    $copias    = $ordenados[1..($ordenados.Count - 1)]

    $linhasRelatorio += "GRUPO DUPLICADO:"
    $linhasRelatorio += "  [MANTIDO]  $original"

    foreach ($copia in $copias) {
        if (-not (Test-Path $copia)) { continue }
        $novo = Mover-Arquivo $copia $pastaDuplicatas
        $msg  = "  [MOVIDO]   $copia -> $novo"
        Write-Host $msg -ForegroundColor Magenta
        $linhasRelatorio += $msg
        $totalDuplicatas++
    }
}

Write-Host "Total de duplicatas movidas: $totalDuplicatas" -ForegroundColor Green

# ============================================================
# RELATORIO FINAL
# ============================================================
$linhasRelatorio += ""
$linhasRelatorio += "============================================"
$linhasRelatorio += " RESUMO FINAL"
$linhasRelatorio += "  Arquivos antigos movidos : $totalAntigos"
$linhasRelatorio += "  Duplicatas movidas       : $totalDuplicatas"
$linhasRelatorio += "  Pasta de revisao         : $pastaRevisao"
$linhasRelatorio += "============================================"

$linhasRelatorio | Out-File -FilePath $relatorio -Encoding UTF8

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " CONCLUIDO!" -ForegroundColor Green
Write-Host " Arquivos antigos movidos : $totalAntigos"
Write-Host " Duplicatas movidas       : $totalDuplicatas"
Write-Host " Tudo esta em: $pastaRevisao"
Write-Host " Relatorio salvo em: $relatorio"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "NENHUM ARQUIVO FOI EXCLUIDO." -ForegroundColor Yellow
Write-Host "Acesse a pasta REVISAO_PARA_EXCLUIR e avalie o que pode deletar."
Write-Host ""
Write-Host "Pressione qualquer tecla para fechar..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
