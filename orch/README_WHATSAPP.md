# orch – WhatsApp Integration Guide (Phase 3) 📱

This guide will help you connect your AI agents directly to your phone using the **Evolution API** bridge.

---

## 🏗️ 1. Start the Messaging Bridge
The easiest way is to run a local bridge using Docker:

```bash
docker run -d --name evolution-api -p 8080:8080 atendaware/evolution-api
```

## 📡 2. Pairing Your Phone
1.  Open your browser to: `http://localhost:8080` (or your Instance URL)
2.  Generate a new Instance (e.g., name it `main`).
3.  **Scan the QR Code** with your personal WhatsApp (Settings > Linked Devices).

## 🗝️ 3. Configure orch
Update your `.env` file with your bridge credentials:

```env
WHATSAPP_API_KEY=your_evolution_api_key_here
WHATSAPP_INSTANCE_URL=http://localhost:8080
WHATSAPP_INSTANCE_NAME=main
WHATSAPP_RECIPIENT=1234567890@s.whatsapp.net  # Your phone number
```

## 🚀 4. Launch the Gateway
Run a simulation and add the `-w` flag:

```bash
python -m orch.cli serve launch --topic "Artificial General Intelligence" --agents "grok" --max-rounds 2 --whatsapp
```

---

> [!TIP]
> **Groups**: You can also send to a WhatsApp Group by finding its **Group JID** (e.g., `1234567890@g.us`) and putting it in the `WHATSAPP_RECIPIENT` field!
