import "dotenv/config";
import { createWhatsAppClient } from "./whatsapp.js";
import { startScheduler } from "./scheduler.js";
import { startApi } from "./api.js";

console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
console.log("   🤖 WhatsApp Motivational Bot");
console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");

if (!process.env.ANTHROPIC_API_KEY) {
  console.error("❌ ANTHROPIC_API_KEY não configurada no arquivo .env");
  process.exit(1);
}

if (!process.env.WHATSAPP_CHANNEL_IDS) {
  console.warn("⚠️  WHATSAPP_CHANNEL_IDS não configurada. Configure no .env antes de usar.\n");
}

// Inicializa WhatsApp
createWhatsAppClient();

// Inicia scheduler de envios automáticos
startScheduler();

// Inicia API de gerenciamento
startApi();

// Graceful shutdown
process.on("SIGINT", () => {
  console.log("\n\n👋 Encerrando bot...");
  process.exit(0);
});

process.on("SIGTERM", () => {
  console.log("\n\n👋 Encerrando bot...");
  process.exit(0);
});
