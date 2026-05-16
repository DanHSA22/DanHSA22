import express from "express";
import { generateContent } from "./content.js";
import { sendToChannels, getConnectionStatus } from "./whatsapp.js";
import { getSchedulerStatus, runSendJob } from "./scheduler.js";

const app = express();
app.use(express.json());

function authMiddleware(req, res, next) {
  const secret = process.env.API_SECRET;
  if (!secret) return next();

  const token = req.headers["x-api-key"];
  if (token !== secret) {
    return res.status(401).json({ erro: "Não autorizado" });
  }
  next();
}

// Status geral
app.get("/status", (req, res) => {
  res.json({
    servico: "whatsapp-motivational-bot",
    whatsapp: getConnectionStatus(),
    scheduler: getSchedulerStatus(),
    horario: new Date().toLocaleString("pt-BR", { timeZone: "America/Sao_Paulo" }),
  });
});

// Prévia do conteúdo (sem enviar)
app.get("/preview", authMiddleware, async (req, res) => {
  try {
    const conteudo = await generateContent();
    res.json({ sucesso: true, conteudo });
  } catch (err) {
    res.status(500).json({ sucesso: false, erro: err.message });
  }
});

// Envio manual imediato
app.post("/send", authMiddleware, async (req, res) => {
  try {
    const resultado = await runSendJob("Manual");
    res.json(resultado);
  } catch (err) {
    res.status(500).json({ sucesso: false, erro: err.message });
  }
});

// Envio de mensagem personalizada
app.post("/send-custom", authMiddleware, async (req, res) => {
  const { mensagem } = req.body;
  if (!mensagem) {
    return res.status(400).json({ erro: "Campo 'mensagem' é obrigatório." });
  }

  try {
    const results = await sendToChannels(mensagem);
    res.json({ sucesso: true, results });
  } catch (err) {
    res.status(500).json({ sucesso: false, erro: err.message });
  }
});

export function startApi() {
  const port = parseInt(process.env.API_PORT || "3000");
  app.listen(port, () => {
    console.log(`🌐 API de gerenciamento rodando em http://localhost:${port}`);
    console.log(`   GET  /status          — Status do bot`);
    console.log(`   GET  /preview         — Prévia do conteúdo`);
    console.log(`   POST /send            — Envio manual`);
    console.log(`   POST /send-custom     — Enviar mensagem personalizada`);
  });
}
