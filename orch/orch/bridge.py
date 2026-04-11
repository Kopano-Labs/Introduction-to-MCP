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
            
        endpoint = f"https://{self.api_key}/send" if self.api_key else "https://whin2.p.rapidapi.com/send"
        
        # Override with pure RapidAPI config if available in env
        rapidapi_key = getattr(settings, "rapidapi_key", self.api_url) # fallback to old env vars
        rapidapi_host = getattr(settings, "rapidapi_whatsapp_host", self.api_key)
        
        headers = {
            "x-rapidapi-key": rapidapi_key,
            "x-rapidapi-host": rapidapi_host,
            "Content-Type": "application/json"
        }
        
        # Whin API payload format
        payload = {
            "text": text
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"https://{rapidapi_host}/send", json=payload, headers=headers)
                if response.status_code in [200, 201]:
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
