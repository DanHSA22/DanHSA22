import pkg from "whatsapp-web.js";
import qrcode from "qrcode-terminal";

const { Client, LocalAuth } = pkg;

let client = null;
let isReady = false;

export function createWhatsAppClient() {
  client = new Client({
    authStrategy: new LocalAuth({ dataPath: "./.wwebjs_auth" }),
    puppeteer: {
      headless: true,
      args: [
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
      ],
    },
  });

  client.on("qr", (qr) => {
    console.log("\n📱 Escaneie o QR Code abaixo com seu WhatsApp:\n");
    qrcode.generate(qr, { small: true });
    console.log("\nAbra o WhatsApp > Dispositivos Conectados > Conectar Dispositivo\n");
  });

  client.on("ready", () => {
    isReady = true;
    console.log("✅ WhatsApp conectado com sucesso!");
  });

  client.on("authenticated", () => {
    console.log("🔐 WhatsApp autenticado!");
  });

  client.on("auth_failure", (msg) => {
    console.error("❌ Falha na autenticação:", msg);
    isReady = false;
  });

  client.on("disconnected", (reason) => {
    console.warn("⚠️  WhatsApp desconectado:", reason);
    isReady = false;
  });

  client.initialize();
  return client;
}

export async function sendToChannels(message) {
  if (!client || !isReady) {
    throw new Error("WhatsApp não está conectado.");
  }

  const rawIds = process.env.WHATSAPP_CHANNEL_IDS || "";
  const channelIds = rawIds
    .split(",")
    .map((id) => id.trim())
    .filter(Boolean);

  if (channelIds.length === 0) {
    throw new Error("Nenhum canal configurado em WHATSAPP_CHANNEL_IDS.");
  }

  const results = [];

  for (const channelId of channelIds) {
    try {
      await client.sendMessage(channelId, message);
      results.push({ channelId, status: "enviado" });
      console.log(`✉️  Mensagem enviada para o canal: ${channelId}`);
    } catch (err) {
      results.push({ channelId, status: "erro", erro: err.message });
      console.error(`❌ Erro ao enviar para ${channelId}:`, err.message);
    }

    // Pausa de 1s entre envios para evitar spam
    await new Promise((r) => setTimeout(r, 1000));
  }

  return results;
}

export function getConnectionStatus() {
  return {
    conectado: isReady,
    cliente: client ? "inicializado" : "não inicializado",
  };
}
