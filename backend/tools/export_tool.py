import logging
import os
from typing import Dict, Any
from backend.tools.security import simulate_rate_limit, sanitize_input_text

logger = logging.getLogger("TripExporter")

async def export_trip(itinerary: Dict[str, Any], format_type: str = "markdown") -> str:
    """
    TripExporter: Formats the generated itinerary into Markdown or HTML.
    
    Args:
        itinerary: The full trip planning output dictionary
        format_type: Output format ('markdown', 'html')
    """
    await simulate_rate_limit()
    
    logger.info(f"Executing TripExporter tool with format_type={format_type}")
    
    city = itinerary["destination"]
    days = itinerary["days"]
    budget = itinerary["budget"]
    hotel = itinerary["hotel"]
    packing = itinerary["packing_list"]
    safety = itinerary["safety_advice"]
    days_data = itinerary["itinerary"]
    
    if format_type.lower() == "html":
        # Generate raw HTML representation
        html = f"""
        <div class="trip-itinerary" style="font-family: sans-serif; padding: 20px; color: #333;">
            <h1 style="color: #4f46e5; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px;">Trip Itinerary for {city.title()}</h1>
            <p><strong>Duration:</strong> {days} Days | <strong>Budget Limit:</strong> ${budget} USD</p>
            
            <div style="background: #f3f4f6; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #1f2937;">Accommodation Selection</h3>
                <p><strong>{hotel['name']}</strong> ({hotel['category']} Hotel)</p>
                <p>Rating: ⭐ {hotel['rating']} | Cost: ${hotel['price_per_night']}/night</p>
                <p><em>{hotel['description']}</em></p>
            </div>
            
            <h2>Daily Schedule</h2>
        """
        for day in days_data:
            html += f"""
            <div style="margin-bottom: 25px; border-left: 4px solid #4f46e5; padding-left: 15px;">
                <h4 style="margin: 0; color: #4f46e5;">Day {day['day']} (Daily Budget: ${day['cost_usd']})</h4>
                <ul style="padding-left: 20px; margin-top: 5px;">
            """
            for slot in day["timeline"]:
                html += f"<li><strong>{slot['time']}:</strong> {slot['name']} ({slot['type']}) - <em>{slot['description']}</em></li>"
            html += "</ul></div>"
            
        html += """</div>"""
        return html
        
    else:
        # Default to Markdown
        md = f"""# ✈️ Trip Itinerary: {city.title()}
        
**Duration:** {days} Days  
**Total Budget:** ${budget} USD  

---

## 🏨 Accommodation Selection
* **Name:** {hotel['name']} ({hotel['category']} Hotel)
* **Rating:** ⭐ {hotel['rating']}/5
* **Price:** ${hotel['price_per_night']} per night
* **Description:** {hotel['description']}

---

## 📅 Day-by-Day Plan

"""
        for day in days_data:
            md += f"### 📍 Day {day['day']} (Daily cost: ${day['cost_usd']})\n"
            for slot in day["timeline"]:
                md += f"* **{slot['time']}** - [{slot['type']}] **{slot['name']}**: {slot['description']} (Cost: ${slot['cost_usd']})\n"
            md += "\n"
            
        md += """---

## 🎒 Packing Checklist
### 🔑 Essentials
"""
        for item in packing.get("essentials", []):
            md += f"- [ ] {item}\n"
            
        md += "\n### 👕 Clothing\n"
        for item in packing.get("clothing", []):
            md += f"- [ ] {item}\n"
            
        md += "\n### ⚙️ Activity Gear\n"
        for item in packing.get("activity_gear", []):
            md += f"- [ ] {item}\n"
            
        md += f"""
---

## 🛡️ Travel Safety & Advice ({city.title()})
### 📞 Emergency Numbers
* **Police:** {safety['emergency_contacts']['police']}
* **Fire & Ambulance:** {safety['emergency_contacts']['fire_ambulance']}
* **Medical Helpline:** {safety['emergency_contacts']['medical_helpline']}

### ⚠️ Local Customs & Norms
"""
        for custom in safety.get("local_customs", []):
            md += f"* {custom}\n"
            
        md += "\n### 🛂 Visa Guidelines\n"
        md += f"{safety.get('visa_guidelines', 'Check local entry requirements before traveling.')}\n"
        
        return md
