import httpx
from typing import Optional, List
from .config import settings
from rich.console import Console

console = Console()

class MessagingBridge:
    def __init__(self):
        self.api_url = getattr(settings, "whatsapp_instance_url", None)
        self.api_key = getattr(settings, "whatsapp_api_key", None)
        self.instance_name = getattr(settings, "whatsapp_instance_name", "main")
        
    def is_configured(self) -> bool:
        return bool(self.api_url and self.api_key)

    async def send_message(self, text: str, recipient: str) -> bool:
        """Send a message to a specific WhatsApp Number/Group JID."""
        if not self.is_configured():
            console.print("[yellow]MessagingBridge: WhatsApp not configured. Skipping external send.[/yellow]")
            return False
            
        endpoint = f"{self.api_url}/message/sendText/{self.instance_name}"
        headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "number": recipient, # Target JID or Phone Number
            "options": {"delay": 1200, "presence": "composing"},
            "text": text
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(endpoint, json=payload, headers=headers)
                if response.status_code == 201:
                    return True
                else:
                    console.print(f"[red]WhatsApp Error ({response.status_code}): {response.text}[/red]")
                    return False
        except Exception as e:
            console.print(f"[red]MessagingBridge Failure: {e}[/red]")
            return False

    async def send_gig_notification(self, gig_data: dict, recipient: str) -> bool:
        title = gig_data.get("title", "New gig")
        location = gig_data.get("location", "nearby")
        payout = gig_data.get("payout", "N/A")
        summary = gig_data.get("summary", "")
        message = (
            f"*New KasiLink Gig*\n"
            f"{title}\n"
            f"Location: {location}\n"
            f"Payout: {payout}\n"
            f"{summary}"
        ).strip()
        return await self.send_message(message, recipient)

    async def send_booking_confirmation(self, booking_data: dict, recipient: str) -> bool:
        message = (
            f"*Booking Confirmed*\n"
            f"{booking_data.get('title', 'Service booking')}\n"
            f"When: {booking_data.get('time', 'TBD')}\n"
            f"Where: {booking_data.get('location', 'TBD')}\n"
            f"Reference: {booking_data.get('reference', 'N/A')}"
        ).strip()
        return await self.send_message(message, recipient)

# Common instance
bridge = MessagingBridge()
