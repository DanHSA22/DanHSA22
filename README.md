# 🤖 WhatsApp Motivational Bot

Bot que envia automaticamente frases motivadoras e recomendações de livros com links de afiliado para canais do WhatsApp.

## ✨ Funcionalidades

- 📅 **Envios automáticos** — 3x por dia (manhã, tarde e noite) com horários configuráveis
- 🤖 **Conteúdo gerado por IA** — Claude API gera frases e recomendações únicas a cada envio
- 📚 **Links de afiliado** — Cada livro recomendado inclui seu link Amazon Associates
- 🌐 **API de gerenciamento** — Envio manual, prévia e status via REST API
- 📱 **Suporte a múltiplos canais** — Envie para vários canais simultaneamente

## 🚀 Instalação

### 1. Clone e instale dependências
```bash
git clone <repo>
cd whatsapp-motivational-bot
npm install
```

### 2. Configure o `.env`
```bash
cp .env.example .env
```

Edite o `.env` com suas configurações:

| Variável | Descrição |
|----------|-----------|
| `ANTHROPIC_API_KEY` | Sua chave da API Claude (console.anthropic.com) |
| `WHATSAPP_CHANNEL_IDS` | IDs dos canais WhatsApp (formato: `12345@newsletter`) |
| `AMAZON_AFFILIATE_ID` | Seu ID de afiliado Amazon (ex: `seuid-20`) |
| `CRON_MORNING` | Cron do envio matinal (padrão: `0 8 * * *`) |
| `CRON_AFTERNOON` | Cron do envio da tarde (padrão: `0 12 * * *`) |
| `CRON_EVENING` | Cron do envio noturno (padrão: `0 19 * * *`) |
| `BOOK_CATEGORY` | Categoria dos livros: `negócios`, `desenvolvimento-pessoal`, `espiritualidade`, `todos` |
| `BOOKS_PER_MESSAGE` | Quantos livros por mensagem (padrão: `2`) |
| `CONTENT_LANGUAGE` | Idioma: `pt-BR`, `en-US`, `es-ES` |
| `API_PORT` | Porta da API de gerenciamento (padrão: `3000`) |
| `API_SECRET` | Chave de acesso à API (deixe vazio para sem autenticação) |

### 3. Encontre o ID do seu canal WhatsApp

Para encontrar o ID do canal, com o WhatsApp Web aberto acesse seu canal.
O ID do canal (newsletter) fica no formato `120363xxxxxxxxxx@newsletter`.

### 4. Inicie o bot
```bash
npm start
```

Escaneie o QR Code que aparecerá no terminal com seu WhatsApp.

## 📡 API de Gerenciamento

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/status` | GET | Status da conexão e scheduler |
| `/preview` | GET | Prévia do próximo conteúdo |
| `/send` | POST | Envio manual imediato |
| `/send-custom` | POST | Enviar mensagem personalizada |

### Exemplo: Envio manual
```bash
curl -X POST http://localhost:3000/send \
  -H "x-api-key: sua-chave-secreta"
```

### Exemplo: Mensagem personalizada
```bash
curl -X POST http://localhost:3000/send-custom \
  -H "Content-Type: application/json" \
  -H "x-api-key: sua-chave-secreta" \
  -d ‘{"mensagem": "Boa tarde! 🌟"}’
```

## 💰 Sistema de Afiliados

Os links de livros são gerados automaticamente com seu ID de afiliado Amazon.
Cada clique e compra feita através dos links gera comissão para você.

**Como se cadastrar:** [Amazon Associates](https://associados.amazon.com.br)

## ⚠️ Importante

- Use este bot apenas em canais onde você é administrador
- Respeite os Termos de Uso do WhatsApp
- O `whatsapp-web.js` é uma biblioteca não-oficial — use com responsabilidade
- Recomendamos não ultrapassar 3-5 envios por dia por canal
