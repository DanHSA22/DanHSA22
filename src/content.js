import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

const AFFILIATE_ID = process.env.AMAZON_AFFILIATE_ID || "seuid-20";
const LANGUAGE = process.env.CONTENT_LANGUAGE || "pt-BR";
const BOOK_CATEGORY = process.env.BOOK_CATEGORY || "todos";
const BOOKS_PER_MESSAGE = parseInt(process.env.BOOKS_PER_MESSAGE || "2");

const LANGUAGE_INSTRUCTIONS = {
  "pt-BR": "Escreva em português do Brasil, de forma calorosa e motivadora.",
  "en-US": "Write in English, in a warm and motivating tone.",
  "es-ES": "Escribe en español, de forma cálida y motivadora.",
};

const CATEGORY_MAP = {
  "negócios": "business, entrepreneurship, leadership, finance",
  "desenvolvimento-pessoal": "self-help, personal development, productivity, mindset",
  "espiritualidade": "spirituality, mindfulness, philosophy, well-being",
  "todos": "business, self-help, personal development, spirituality, leadership, productivity",
};

function buildAmazonLink(searchQuery) {
  const query = encodeURIComponent(searchQuery);
  return `https://www.amazon.com.br/s?k=${query}&tag=${AFFILIATE_ID}`;
}

export async function generateContent() {
  const langInstruction = LANGUAGE_INSTRUCTIONS[LANGUAGE] || LANGUAGE_INSTRUCTIONS["pt-BR"];
  const categories = CATEGORY_MAP[BOOK_CATEGORY] || CATEGORY_MAP["todos"];
  const today = new Date().toLocaleDateString("pt-BR", {
    weekday: "long",
    day: "numeric",
    month: "long",
  });

  const prompt = `Você é um curador de conteúdo motivacional para um canal do WhatsApp.
Hoje é ${today}.

${langInstruction}

Crie uma mensagem para um canal do WhatsApp com:

1. Uma saudação adequada ao horário (manhã, tarde ou noite)
2. Uma frase motivadora poderosa e original (não use clichês batidos)
3. Uma breve reflexão de 2-3 frases relacionada à frase
4. Recomendação de exatamente ${BOOKS_PER_MESSAGE} livros das categorias: ${categories}

Para cada livro, inclua:
- Título e autor
- Por que ler (máx 2 frases)
- Uma lição principal do livro

Retorne a resposta ESTRITAMENTE neste formato JSON:
{
  "saudacao": "...",
  "frase_motivadora": "...",
  "reflexao": "...",
  "livros": [
    {
      "titulo": "...",
      "autor": "...",
      "por_que_ler": "...",
      "licao_principal": "...",
      "search_query": "titulo autor livro"
    }
  ]
}

Certifique-se que o JSON seja válido. Não inclua nada fora do JSON.`;

  const response = await client.messages.create({
    model: "claude-haiku-4-5",
    max_tokens: 1024,
    messages: [{ role: "user", content: prompt }],
  });

  const text = response.content.find((b) => b.type === "text")?.text || "";

  let data;
  try {
    const jsonMatch = text.match(/\{[\s\S]*\}/);
    data = JSON.parse(jsonMatch ? jsonMatch[0] : text);
  } catch {
    throw new Error(`Falha ao parsear resposta da Claude: ${text}`);
  }

  return formatMessage(data);
}

function formatMessage(data) {
  const { saudacao, frase_motivadora, reflexao, livros } = data;

  let msg = `${saudacao}\n\n`;
  msg += `💬 *${frase_motivadora}*\n\n`;
  msg += `${reflexao}\n\n`;
  msg += `📚 *Livros que vão mudar sua vida:*\n\n`;

  livros.forEach((livro, i) => {
    const link = buildAmazonLink(livro.search_query || `${livro.titulo} ${livro.autor}`);
    msg += `${i + 1}️⃣ *${livro.titulo}*\n`;
    msg += `_por ${livro.autor}_\n`;
    msg += `✅ Por que ler: ${livro.por_que_ler}\n`;
    msg += `💡 Lição: _${livro.licao_principal}_\n`;
    msg += `🛒 Adquira aqui: ${link}\n\n`;
  });

  msg += `━━━━━━━━━━━━━━━━━━━\n`;
  msg += `_Conteúdo enviado automaticamente. Compras via links apóiam este canal._ 🙏`;

  return msg;
}
