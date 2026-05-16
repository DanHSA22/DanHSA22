import cron from "node-cron";
import { generateContent } from "./content.js";
import { sendToChannels } from "./whatsapp.js";

const activeTasks = [];

async function runSendJob(label) {
  console.log(`\n⏰ [${label}] Iniciando envio agendado...`);

  try {
    console.log("🤖 Gerando conteúdo com Claude...");
    const message = await generateContent();

    console.log("📤 Enviando para os canais WhatsApp...");
    const results = await sendToChannels(message);

    const sucessos = results.filter((r) => r.status === "enviado").length;
    const erros = results.filter((r) => r.status === "erro").length;

    console.log(`✅ [${label}] Concluído: ${sucessos} enviado(s), ${erros} erro(s)\n`);
    return { sucesso: true, results };
  } catch (err) {
    console.error(`❌ [${label}] Falha no envio:`, err.message);
    return { sucesso: false, erro: err.message };
  }
}

export function startScheduler() {
  const schedules = [
    { env: "CRON_MORNING", default: "0 8 * * *", label: "Manhã" },
    { env: "CRON_AFTERNOON", default: "0 12 * * *", label: "Tarde" },
    { env: "CRON_EVENING", default: "0 19 * * *", label: "Noite" },
  ];

  for (const { env, default: fallback, label } of schedules) {
    const expression = process.env[env] || fallback;

    if (!cron.validate(expression)) {
      console.warn(`⚠️  Expressão cron inválida para ${env}: "${expression}". Usando padrão.`);
    }

    const task = cron.schedule(expression, () => runSendJob(label), {
      timezone: "America/Sao_Paulo",
    });

    activeTasks.push({ label, expression, task });
    console.log(`📅 Agendado [${label}]: ${expression}`);
  }

  console.log(`\n🚀 Scheduler iniciado com ${activeTasks.length} tarefa(s)\n`);
}

export function stopScheduler() {
  activeTasks.forEach(({ task }) => task.destroy());
  activeTasks.length = 0;
  console.log("🛑 Scheduler parado.");
}

export function getSchedulerStatus() {
  return activeTasks.map(({ label, expression }) => ({ label, expression }));
}

export { runSendJob };
