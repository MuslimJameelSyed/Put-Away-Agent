"""
🏭 AGENTIC AI PUT-AWAY DECISION SYSTEM
Real-time storage location recommendation with safety guarantees

Production-Ready Warehouse AI System
Powered by OpenRouter LLM API


"""

import streamlit as st
import time
from datetime import datetime
from typing import Dict, List
import re

# ============================================================================
# 🔑 API CONFIGURATION (EMBEDDED - NO UI EXPOSURE)
# ============================================================================

# LLM Backend Configuration
USE_OLLAMA = False  # Set to True to use local Ollama, False to use OpenRouter

# Ollama Configuration
OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_MODEL = "phi3:mini"  # The model you pulled from Ollama

# OpenRouter Configuration (backup)
# Load API key from Streamlit secrets or environment variables
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "") if hasattr(st, 'secrets') else ""
OPENROUTER_MODEL = "microsoft/phi-3-mini-128k-instruct"

# ============================================================================
# CATEGORY INFERENCE RULES (INTELLIGENT DEFAULTS)
# ============================================================================

CATEGORY_RULES = {
    'Frozen Food': {
        'temp_default': 'frozen',
        'hazard_default': 'none',
        'description': 'Perishable food requiring -18°C storage'
    },
    'Chemicals': {
        'temp_default': 'ambient',
        'hazard_default': 'corrosive',
        'description': 'May contain hazardous substances'
    },
    'Pharmaceuticals': {
        'temp_default': 'controlled',
        'hazard_default': 'none',
        'description': 'Temperature-sensitive medical products'
    },
    'Electronics': {
        'temp_default': 'ambient',
        'hazard_default': 'none',
        'description': 'Standard electronics goods'
    },
    'Machinery': {
        'temp_default': 'ambient',
        'hazard_default': 'none',
        'description': 'Heavy industrial equipment'
    },
    'Textiles': {
        'temp_default': 'ambient',
        'hazard_default': 'none',
        'description': 'Fabric and clothing items'
    },
    'Automotive': {
        'temp_default': 'ambient',
        'hazard_default': 'none',
        'description': 'Auto parts and components'
    },
    'General Goods': {
        'temp_default': 'ambient',
        'hazard_default': 'none',
        'description': 'Standard merchandise'
    }
}

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="AI Put-Away System",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# ZONE MASTER DATA (REALISTIC WAREHOUSE CONFIGURATION)
# ============================================================================

ZONES = {
    'A': {
        'name': 'General Storage',
        'type': 'ambient',
        'max_weight': 500,
        'temp_range': '15-25°C',
        'fire_safe': False,
        'dispatch_distance': 50,
        'rack_type': 'Selective Pallet Rack',
        'equipment': 'Forklift, Pallet Jack'
    },
    'B': {
        'name': 'Cold Storage',
        'type': 'refrigerated',
        'max_weight': 300,
        'temp_range': '-25 to 4°C',
        'fire_safe': False,
        'dispatch_distance': 80,
        'rack_type': 'Drive-In Rack',
        'equipment': 'Cold-rated Forklift'
    },
    'C': {
        'name': 'Hazmat Area',
        'type': 'fire_safe',
        'max_weight': 400,
        'temp_range': '15-20°C',
        'fire_safe': True,
        'dispatch_distance': 120,
        'rack_type': 'Containment Pallet Rack',
        'equipment': 'Explosion-proof Forklift'
    },
    'D': {
        'name': 'Fast-Pick Zone',
        'type': 'ambient',
        'max_weight': 50,
        'temp_range': '18-22°C',
        'fire_safe': False,
        'dispatch_distance': 15,
        'rack_type': 'Carton Flow Rack',
        'equipment': 'Pick Cart, Conveyor'
    },
    'E': {
        'name': 'Bulk & Heavy',
        'type': 'reinforced',
        'max_weight': 2500,
        'temp_range': '10-30°C',
        'fire_safe': False,
        'dispatch_distance': 90,
        'rack_type': 'Heavy-Duty Cantilever',
        'equipment': 'Heavy Forklift, Crane'
    }
}

# ============================================================================
# PRODUCT CATALOG (PREDEFINED PRODUCTS FOR QUICK SELECTION)
# ============================================================================

PRODUCT_CATALOG = {
    "Industrial Solvent (Flammable)": {
        "category": "Chemicals",
        "weight": 25.0,
        "hazard": "flammable",
        "temp": "ambient",
        "turnover": "medium"
    },
    "Frozen Vegetables - 20kg Case": {
        "category": "Frozen Food",
        "weight": 20.0,
        "hazard": "none",
        "temp": "frozen",
        "turnover": "high"
    },
    "Smartphone - iPhone 15 Pro": {
        "category": "Electronics",
        "weight": 2.5,
        "hazard": "none",
        "temp": "ambient",
        "turnover": "high"
    },
    "Industrial Motor - 800kg": {
        "category": "Machinery",
        "weight": 800.0,
        "hazard": "none",
        "temp": "ambient",
        "turnover": "low"
    },
    "Laptop - Dell XPS 13": {
        "category": "Electronics",
        "weight": 3.0,
        "hazard": "none",
        "temp": "ambient",
        "turnover": "high"
    },
    "Frozen Pizza - Bulk Pack": {
        "category": "Frozen Food",
        "weight": 15.0,
        "hazard": "none",
        "temp": "frozen",
        "turnover": "high"
    },
    "Hydrochloric Acid 5L": {
        "category": "Chemicals",
        "weight": 6.5,
        "hazard": "corrosive",
        "temp": "ambient",
        "turnover": "low"
    },
    "Insulin Vials - Refrigerated": {
        "category": "Pharmaceuticals",
        "weight": 1.2,
        "hazard": "none",
        "temp": "cold",
        "turnover": "medium"
    },
    "Cotton T-Shirts - 100pc Carton": {
        "category": "Textiles",
        "weight": 25.0,
        "hazard": "none",
        "temp": "ambient",
        "turnover": "medium"
    },
    "Car Engine Block - V6": {
        "category": "Automotive",
        "weight": 180.0,
        "hazard": "none",
        "temp": "ambient",
        "turnover": "low"
    },
    "Lithium Battery Pack - Industrial": {
        "category": "Electronics",
        "weight": 45.0,
        "hazard": "flammable",
        "temp": "ambient",
        "turnover": "medium"
    },
    "Steel Beams - 2500kg Pallet": {
        "category": "Machinery",
        "weight": 2500.0,
        "hazard": "none",
        "temp": "ambient",
        "turnover": "low"
    },
    "Frozen Seafood - Premium Pack": {
        "category": "Frozen Food",
        "weight": 30.0,
        "hazard": "none",
        "temp": "frozen",
        "turnover": "medium"
    },
    "Medical Equipment - Sterile": {
        "category": "Pharmaceuticals",
        "weight": 8.0,
        "hazard": "none",
        "temp": "controlled",
        "turnover": "medium"
    },
    "Paint Thinner - 25L Drum": {
        "category": "Chemicals",
        "weight": 22.0,
        "hazard": "flammable",
        "temp": "ambient",
        "turnover": "low"
    },
    "Gaming Console - PS5": {
        "category": "Electronics",
        "weight": 4.5,
        "hazard": "none",
        "temp": "ambient",
        "turnover": "high"
    },
    "Winter Jackets - 50pc Box": {
        "category": "Textiles",
        "weight": 35.0,
        "hazard": "none",
        "temp": "ambient",
        "turnover": "medium"
    },
    "Brake Pads - Assorted Set": {
        "category": "Automotive",
        "weight": 12.0,
        "hazard": "none",
        "temp": "ambient",
        "turnover": "high"
    },
    "Ammonia Solution - 10L": {
        "category": "Chemicals",
        "weight": 11.0,
        "hazard": "toxic",
        "temp": "ambient",
        "turnover": "low"
    },
    "Industrial Forklift Battery": {
        "category": "Machinery",
        "weight": 650.0,
        "hazard": "none",
        "temp": "ambient",
        "turnover": "low"
    }
}

# ============================================================================
# INPUT VALIDATION & INFERENCE
# ============================================================================

def validate_item_inputs(category: str, temperature_req: str, hazard_class: str) -> List[str]:
    """
    Validate item inputs and detect conflicts between category and selections.
    Returns list of warning messages.
    """
    warnings = []

    if category in CATEGORY_RULES:
        expected_temp = CATEGORY_RULES[category]['temp_default']
        expected_hazard = CATEGORY_RULES[category]['hazard_default']

        # Check temperature mismatch
        if expected_temp == 'frozen' and temperature_req not in ['frozen', 'cold']:
            warnings.append(f"⚠️ CRITICAL: '{category}' typically requires FROZEN/COLD storage, but '{temperature_req}' is selected!")
        elif expected_temp == 'cold' and temperature_req == 'ambient':
            warnings.append(f"⚠️ WARNING: '{category}' usually needs cold storage, but 'ambient' is selected.")
        elif expected_temp == 'controlled' and temperature_req == 'ambient':
            warnings.append(f"⚠️ NOTICE: '{category}' may need controlled temperature, but 'ambient' is selected.")

        # Check hazard mismatch
        if expected_hazard != 'none' and hazard_class == 'none':
            warnings.append(f"⚠️ WARNING: '{category}' may contain hazardous materials. Consider reviewing hazard classification.")

    return warnings

# ============================================================================
# RULE ENGINE (SAFETY-FIRST ARCHITECTURE)
# ============================================================================

def apply_safety_rules(item: Dict) -> Dict:
    """
    Hard constraint enforcement BEFORE LLM.
    Safety rules are non-negotiable.
    """
    eligible_zones = list(ZONES.keys())
    rejected_zones = []
    mandatory_zone = None
    
    safety_checks = {
        'fire_safety': {'status': True, 'message': 'No hazardous materials detected'},
        'weight_limit': {'status': True, 'message': f"Weight {item['weight']}kg within limits"},
        'temp_requirement': {'status': True, 'message': 'Ambient storage acceptable'},
        'dispatch_proximity': {'status': True, 'message': 'Standard dispatch routing'}
    }
    
    # RULE 1: Hazardous Materials → Zone C (MANDATORY)
    if item['hazard_class'] in ['flammable', 'corrosive', 'toxic', 'explosive', 'oxidizer']:
        mandatory_zone = 'C'
        eligible_zones = ['C']
        safety_checks['fire_safety'] = {
            'status': True, 
            'message': f"HAZMAT protocol: {item['hazard_class'].upper()} routed to fire-safe zone"
        }
        for z in ['A', 'B', 'D', 'E']:
            rejected_zones.append({
                'zone': z, 
                'reason': f"Not certified for {item['hazard_class']} materials",
                'regulation': 'OSHA 1910.106 / EPA 40 CFR'
            })
    
    # RULE 2: Cold Chain → Zone B (MANDATORY)
    elif item['temperature_req'] in ['cold', 'frozen', 'chilled']:
        mandatory_zone = 'B'
        eligible_zones = ['B']
        safety_checks['temp_requirement'] = {
            'status': True, 
            'message': f"Cold chain required: {item['temperature_req'].upper()} storage activated"
        }
        for z in ['A', 'C', 'D', 'E']:
            rejected_zones.append({
                'zone': z, 
                'reason': 'No temperature control capability',
                'regulation': 'FDA 21 CFR 110 / HACCP'
            })
    
    # RULE 3: Weight Constraints
    else:
        weight = item['weight']
        for zone_id in list(eligible_zones):
            max_w = ZONES[zone_id]['max_weight']
            if weight > max_w:
                eligible_zones.remove(zone_id)
                rejected_zones.append({
                    'zone': zone_id, 
                    'reason': f"Exceeds {max_w}kg limit (item: {weight}kg)",
                    'regulation': 'Rack capacity spec'
                })
        
        if weight > 500:
            safety_checks['weight_limit'] = {
                'status': True, 
                'message': f"Heavy item ({weight}kg) → reinforced zone required"
            }
    
    # RULE 4: High turnover preference
    if item['turnover_rate'] == 'high' and 'D' in eligible_zones and item['weight'] < 50:
        safety_checks['dispatch_proximity'] = {
            'status': True, 
            'message': 'High-velocity SKU → fast-pick zone recommended'
        }
    
    return {
        'eligible_zones': eligible_zones,
        'rejected_zones': rejected_zones,
        'safety_checks': safety_checks,
        'mandatory_zone': mandatory_zone
    }

# Template-based reasoning function removed - now using LLM-generated reasoning directly

# ============================================================================
# LLM CALL (OPENROUTER)
# ============================================================================

def call_llm(item: Dict, eligible_zones: List[str]) -> Dict:
    """
    Call OpenRouter API for intelligent zone selection with detailed reasoning.
    Falls back to rule-based if API unavailable.
    """

    print(f"\n[LLM] call_llm() invoked for item: {item.get('product_name', 'Unknown')}")
    print(f"   Eligible zones: {eligible_zones}")

    # Determine which LLM backend to use
    if USE_OLLAMA:
        print(f"   [OLLAMA] Using Ollama (local) - Model: {OLLAMA_MODEL}")
    else:
        print(f"   [OPENROUTER] Using OpenRouter - API Key configured: {bool(OPENROUTER_API_KEY)}")

    try:
        from openai import OpenAI

        # Initialize client based on backend selection
        if USE_OLLAMA:
            print(f"   [INIT] Initializing Ollama client at {OLLAMA_BASE_URL}...")
            client = OpenAI(
                base_url=OLLAMA_BASE_URL,
                api_key="ollama"  # Ollama doesn't need real API key but OpenAI client requires one
            )
            model = OLLAMA_MODEL
        else:
            # Check if OpenRouter API key is configured
            if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "sk-or-v1-your-api-key-here":
                print("   [WARNING] OpenRouter API key not configured - using fallback")
                return rule_based_selection(item, eligible_zones)

            print(f"   [INIT] Initializing OpenRouter client...")
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=OPENROUTER_API_KEY
            )
            model = OPENROUTER_MODEL

        print("   [SUCCESS] Client initialized")

        # Build detailed zone descriptions
        zones_desc = "\n".join([
            f"Zone {z}: {ZONES[z]['name']}\n"
            f"  - Type: {ZONES[z]['type']}\n"
            f"  - Max Weight: {ZONES[z]['max_weight']}kg\n"
            f"  - Temperature: {ZONES[z]['temp_range']}\n"
            f"  - Rack: {ZONES[z]['rack_type']}\n"
            f"  - Equipment: {ZONES[z]['equipment']}\n"
            f"  - Dispatch Distance: {ZONES[z]['dispatch_distance']}m\n"
            for z in eligible_zones
        ])

        # Check if only one zone available (mandatory assignment)
        if len(eligible_zones) == 1:
            prompt = f"""You are an expert warehouse management AI agent. Explain why this item MUST be stored in the designated zone.

INCOMING ITEM DETAILS:
- Product Name: {item['product_name']}
- Category: {item['category']}
- Weight: {item['weight']}kg
- Hazard Classification: {item['hazard_class']}
- Temperature Requirement: {item['temperature_req']}
- Turnover Rate: {item['turnover_rate']}

DESIGNATED ZONE:
{zones_desc}

This zone assignment is MANDATORY due to safety regulations. Explain in 2-3 detailed sentences WHY this specific item requires this zone, referencing the item's properties and the zone's specialized capabilities.

Respond in this EXACT format:

ZONE: {eligible_zones[0]}
CONFIDENCE: high
REASONING: [Provide detailed explanation about why this item's specific characteristics (hazard class, temperature needs, weight, etc.) require this zone's specialized features (temperature control, fire safety, equipment, etc.). Be specific and technical.]"""
        else:
            prompt = f"""You are an expert warehouse management AI agent. Your task is to select the optimal storage zone for an incoming item and provide detailed reasoning.

INCOMING ITEM DETAILS:
- Product Name: {item['product_name']}
- Category: {item['category']}
- Weight: {item['weight']}kg
- Hazard Classification: {item['hazard_class']}
- Temperature Requirement: {item['temperature_req']}
- Turnover Rate: {item['turnover_rate']}

AVAILABLE ZONES (after safety filtering):
{zones_desc}

DECISION CRITERIA:
1. Safety compliance (hazmat regulations, weight limits, temperature control)
2. Operational efficiency (pick time, dispatch distance)
3. Space utilization (rack type compatibility)
4. Equipment availability (handling requirements)

Provide your recommendation in this EXACT format:

ZONE: [single letter A-E from available zones]
CONFIDENCE: [high/medium/low]
REASONING: [Provide 2-3 sentences explaining why this zone is optimal for this specific item, considering its weight, turnover rate, handling requirements, and operational benefits. Reference specific zone characteristics like rack type, equipment, or dispatch distance.]"""

        print(f"   [API] Calling LLM API: {model}")
        start = time.time()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a warehouse optimization expert. Provide zone recommendations with detailed reasoning."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        decision_time = time.time() - start
        print(f"   [TIMING] API responded in {decision_time:.2f}s")

        # Debug: Check response structure
        print(f"   Response type: {type(response)}")
        print(f"   Has choices: {hasattr(response, 'choices')}")
        print(f"   Choices length: {len(response.choices) if hasattr(response, 'choices') else 0}")

        if response.choices and len(response.choices) > 0:
            print(f"   First choice: {response.choices[0]}")
            print(f"   Message: {response.choices[0].message}")
            text = response.choices[0].message.content
            print(f"   Content type: {type(text)}")
            print(f"   Content length: {len(text) if text else 0}")
        else:
            text = ""

        # Debug: Print raw LLM response
        print(f"\n=== LLM RAW RESPONSE ===\n{text}\n========================\n")

        # Validate response is not empty
        if not text or len(text.strip()) < 10:
            print("   [WARNING] LLM returned empty or very short response - returning error")
            return {
                'zone': None,
                'confidence': 'low',
                'reasoning': None,
                'decision_time': time.time() - start,
                'success': False,
                'error': 'LLM returned empty or invalid response. Please try again.'
            }

        # Parse zone
        zone_match = re.search(r'ZONE:\s*([A-E])', text, re.IGNORECASE)
        zone = zone_match.group(1).upper() if zone_match else eligible_zones[0]

        if zone not in eligible_zones:
            zone = eligible_zones[0]

        # Parse confidence
        conf_match = re.search(r'CONFIDENCE:\s*(high|medium|low)', text, re.IGNORECASE)
        confidence = conf_match.group(1).lower() if conf_match else 'medium'

        # Parse reasoning
        reasoning_match = re.search(r'REASONING:\s*(.+?)(?:\n\n|\Z)', text, re.IGNORECASE | re.DOTALL)
        reasoning = reasoning_match.group(1).strip() if reasoning_match else text

        # Clean up reasoning (remove extra whitespace)
        reasoning = ' '.join(reasoning.split())

        # Debug: Print parsed reasoning
        print(f"=== PARSED REASONING ===\n{reasoning}\n========================\n")

        return {
            'zone': zone,
            'confidence': confidence,
            'reasoning': reasoning,
            'decision_time': decision_time,
            'success': True,
            'llm_backend': 'Ollama (phi3:mini)' if USE_OLLAMA else 'OpenRouter (Mistral-7B)',
            'llm_model': model
        }

    except Exception as e:
        # Log error for debugging
        print(f"\n[ERROR] LLM Error occurred!")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        import traceback
        print(f"   Traceback:\n{traceback.format_exc()}")

        # Return error instead of fallback
        return {
            'zone': None,
            'confidence': 'low',
            'reasoning': None,
            'decision_time': 0,
            'success': False,
            'error': f'API Error: {type(e).__name__} - {str(e)}'
        }

def rule_based_selection(item: Dict, eligible_zones: List[str]) -> Dict:
    """
    Intelligent fallback when LLM unavailable.
    Generates rule-based reasoning instead of templates.
    """
    print("   [FALLBACK] Using rule-based fallback selection")
    weight = item['weight']
    turnover = item['turnover_rate']
    category = item['category']

    # Priority logic with reasoning
    if weight > 500 and 'E' in eligible_zones:
        zone = 'E'
        confidence = 'high'
        reasoning = f"Heavy item ({weight}kg) requires Zone E's reinforced infrastructure with {ZONES['E']['max_weight']}kg capacity, heavy-duty equipment, and structural support for safe handling."
    elif turnover == 'high' and weight < 50 and 'D' in eligible_zones:
        zone = 'D'
        confidence = 'high'
        reasoning = f"High-turnover {category} item optimally placed in Zone D fast-pick area. Close dispatch proximity ({ZONES['D']['dispatch_distance']}m) and {ZONES['D']['rack_type']} maximize picking efficiency."
    elif turnover == 'medium' and 'A' in eligible_zones:
        zone = 'A'
        confidence = 'medium'
        reasoning = f"Standard {category} item with medium turnover suited for Zone A general storage. {ZONES['A']['rack_type']} provides flexible slotting with balanced accessibility."
    else:
        zone = eligible_zones[0] if eligible_zones else 'A'
        confidence = 'medium'
        zone_info = ZONES[zone]
        reasoning = f"Item assigned to Zone {zone} ({zone_info['name']}) based on operational constraints. {zone_info['rack_type']} compatible with {weight}kg load."

    return {
        'zone': zone,
        'confidence': confidence,
        'reasoning': reasoning,
        'decision_time': 0.05,
        'success': True
    }

# ============================================================================
# MAIN AGENT FUNCTION
# ============================================================================

def run_agent(item: Dict) -> Dict:
    """
    Complete agent pipeline: Rules → LLM → Validation → Response
    """
    start_time = time.time()

    # Step 1: Apply safety rules
    rules_result = apply_safety_rules(item)

    # Step 2: Always call LLM for reasoning, even for mandatory assignments
    if rules_result['mandatory_zone']:
        # Mandatory zone - zone is predetermined but LLM explains why
        zone = rules_result['mandatory_zone']
        confidence = 'high'
        mandatory = True

        # Still call LLM to get contextual reasoning for the mandatory assignment
        llm_result = call_llm(item, [zone])  # Pass only the mandatory zone

        # Check if LLM failed
        if not llm_result.get('success', True):
            return {
                'success': False,
                'error': llm_result.get('error', 'Unknown error occurred'),
                'safety_checks': rules_result['safety_checks'],
                'rejected_zones': rules_result['rejected_zones'],
                'eligible_zones': rules_result['eligible_zones']
            }

        reasoning = llm_result['reasoning']
        decision_time = llm_result['decision_time']
    else:
        # LLM-based decision for operational optimization
        llm_result = call_llm(item, rules_result['eligible_zones'])

        # Check if LLM failed
        if not llm_result.get('success', True):
            return {
                'success': False,
                'error': llm_result.get('error', 'Unknown error occurred'),
                'safety_checks': rules_result['safety_checks'],
                'rejected_zones': rules_result['rejected_zones'],
                'eligible_zones': rules_result['eligible_zones']
            }

        zone = llm_result['zone']
        confidence = llm_result['confidence']
        reasoning = llm_result['reasoning']
        decision_time = llm_result['decision_time']
        mandatory = False

    # Calculate total time
    total_time = time.time() - start_time

    return {
        'success': True,
        'zone': zone,
        'zone_name': ZONES[zone]['name'],
        'zone_details': ZONES[zone],
        'confidence': confidence,
        'reasoning': reasoning,
        'decision_time': round(decision_time, 3),
        'safety_checks': rules_result['safety_checks'],
        'rejected_zones': rules_result['rejected_zones'],
        'mandatory': mandatory,
        'eligible_zones': rules_result['eligible_zones']
    }

# ============================================================================
# CUSTOM CSS 
# ============================================================================

st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Header */
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 1.8rem 2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1rem;
        opacity: 0.9;
    }
    
    .status-badge {
        display: inline-block;
        background: rgba(255,255,255,0.2);
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        margin-top: 0.8rem;
    }
    
    /* Cards */
    .card {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        border: 1px solid #e8e8e8;
        height: 100%;
    }
    
    .card-header {
        font-size: 1.15rem;
        font-weight: 600;
        color: #1e3c72;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid #1e3c72;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Zone Display */
    .zone-display {
        background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%);
        color: white;
        padding: 1.8rem;
        border-radius: 12px;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 6px 20px rgba(0, 176, 155, 0.3);
    }
    
    .zone-display.mandatory {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        box-shadow: 0 6px 20px rgba(245, 87, 108, 0.3);
    }
    
    .zone-label {
        font-size: 0.85rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .zone-code {
        font-size: 3rem;
        font-weight: 800;
        margin: 0.3rem 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .zone-name {
        font-size: 1.1rem;
        opacity: 0.95;
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.8rem;
        margin: 0.3rem;
    }
    
    .badge-high { background: #d4edda; color: #155724; }
    .badge-medium { background: #fff3cd; color: #856404; }
    .badge-low { background: #f8d7da; color: #721c24; }
    .badge-time { background: #1e3c72; color: white; }
    .badge-mandatory { background: #f5576c; color: white; }
    
    /* Safety Checks */
    .safety-item {
        padding: 0.6rem 0.8rem;
        margin: 0.4rem 0;
        border-radius: 8px;
        font-size: 0.9rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .safety-item.passed {
        background: linear-gradient(90deg, #d4edda 0%, #f8f9fa 100%);
        border-left: 4px solid #28a745;
    }
    
    .safety-item.warning {
        background: linear-gradient(90deg, #fff3cd 0%, #f8f9fa 100%);
        border-left: 4px solid #ffc107;
    }
    
    .safety-item .icon { font-size: 1.1rem; }
    .safety-item .text { flex: 1; }
    .safety-item .label { font-weight: 600; color: #333; }
    .safety-item .detail { font-size: 0.8rem; color: #666; margin-top: 2px; }
    
    /* Reasoning Box */
    .reasoning-box {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1rem 1.2rem;
        border-radius: 10px;
        border-left: 4px solid #1e3c72;
        margin: 1rem 0;
        font-size: 0.95rem;
        line-height: 1.6;
        color: #333;
    }
    
    /* Rejected Zones */
    .rejected-zone {
        background: #fff5f5;
        padding: 0.5rem 0.8rem;
        margin: 0.3rem 0;
        border-radius: 6px;
        border-left: 3px solid #dc3545;
        font-size: 0.85rem;
    }
    
    .rejected-zone .zone-id { font-weight: 700; color: #dc3545; }
    .rejected-zone .reason { color: #666; }
    
    /* Override Section */
    .override-section {
        background: linear-gradient(135deg, #fff9e6 0%, #fff3cd 100%);
        padding: 1.2rem 1.5rem;
        border-radius: 12px;
        border: 2px solid #ffc107;
        margin: 1.5rem 0;
    }
    
    .override-section h3 {
        margin: 0 0 1rem 0;
        color: #856404;
        font-size: 1.1rem;
    }
    
    /* Audit Log */
    .audit-header {
        background: #1e3c72;
        color: white;
        padding: 0.6rem 1rem;
        border-radius: 8px 8px 0 0;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .audit-row {
        padding: 0.6rem 1rem;
        border-bottom: 1px solid #eee;
        font-size: 0.85rem;
        display: flex;
        align-items: center;
    }
    
    .audit-row:nth-child(even) { background: #f8f9fa; }
    .audit-row:hover { background: #e9ecef; }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(30, 60, 114, 0.3);
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(30, 60, 114, 0.4);
    }
    
    /* Zone Details */
    .zone-detail {
        font-size: 0.8rem;
        color: #666;
        margin-top: 0.5rem;
        padding: 0.5rem;
        background: #f8f9fa;
        border-radius: 6px;
    }
    
    .zone-detail-item {
        display: flex;
        justify-content: space-between;
        padding: 0.2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE
# ============================================================================

if 'audit_log' not in st.session_state:
    st.session_state.audit_log = []
if 'last_result' not in st.session_state:
    st.session_state.last_result = None
if 'last_item' not in st.session_state:
    st.session_state.last_item = None

# ============================================================================
# HEADER
# ============================================================================

current_time = datetime.now().strftime("%H:%M:%S")
st.markdown(f"""
<div class="main-header">
    <h1>AGENTIC AI PUT-AWAY DECISION SYSTEM</h1>
    <p>Real-time storage location recommendation with safety guarantees</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# MAIN LAYOUT
# ============================================================================

col1, col2, col3 = st.columns([1, 1.2, 1])

# ──────────────────────────────────────────────────────────────────────────
# COLUMN 1: INCOMING ITEM INPUT
# ──────────────────────────────────────────────────────────────────────────

with col1:
    st.markdown("""
    <div class="card">
        <div class="card-header">📦 Incoming Item</div>
    """, unsafe_allow_html=True)
    
    st.caption("WMS / Operator Input")
    
    item_id = st.text_input(
        "Item ID / SKU",
        value=f"SKU-{datetime.now().strftime('%y%m%d-%H%M%S')}",
        help="Unique identifier for tracking"
    )

    # Product selection with auto-population
    product_name = st.selectbox(
        "Product Name",
        options=list(PRODUCT_CATALOG.keys()),
        index=0,
        help="Select from predefined product catalog"
    )

    # Get product defaults from catalog
    product_defaults = PRODUCT_CATALOG.get(product_name, {})

    category = st.selectbox(
        "Category",
        ["Electronics", "Frozen Food", "Chemicals", "Machinery",
         "Pharmaceuticals", "Textiles", "Automotive", "General Goods"],
        index=["Electronics", "Frozen Food", "Chemicals", "Machinery",
               "Pharmaceuticals", "Textiles", "Automotive", "General Goods"].index(product_defaults.get("category", "Electronics")),
        help="Product category for analytics"
    )

    weight = st.number_input(
        "Weight (kg)",
        min_value=0.1,
        max_value=3000.0,
        value=float(product_defaults.get("weight", 45.0)),
        step=0.5,
        help="Total item weight including packaging"
    )

    hazard_options = ["none", "flammable", "corrosive", "toxic", "explosive", "oxidizer"]
    hazard_class = st.selectbox(
        "Hazard Classification",
        hazard_options,
        index=hazard_options.index(product_defaults.get("hazard", "none")),
        help="UN hazard classification if applicable"
    )

    temp_options = ["ambient", "cold", "frozen", "chilled", "controlled"]
    temperature_req = st.selectbox(
        "Temperature Requirement",
        temp_options,
        index=temp_options.index(product_defaults.get("temp", "ambient")),
        help="Storage temperature requirement"
    )

    turnover_options = ["low", "medium", "high"]
    turnover_rate = st.selectbox(
        "Turnover Rate",
        turnover_options,
        index=turnover_options.index(product_defaults.get("turnover", "medium")),
        help="Expected pick frequency"
    )

    st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)

    # Validate inputs and show warnings
    warnings = validate_item_inputs(category, temperature_req, hazard_class)
    if warnings:
        for warning in warnings:
            st.warning(warning, icon="⚠️")

    st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)

    recommend_btn = st.button("🚀 GET RECOMMENDATION", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────
# PROCESS RECOMMENDATION
# ──────────────────────────────────────────────────────────────────────────

if recommend_btn:
    item = {
        'item_id': item_id,
        'product_name': product_name,
        'category': category,
        'weight': weight,
        'hazard_class': hazard_class,
        'temperature_req': temperature_req,
        'turnover_rate': turnover_rate
    }

    with st.spinner("🔄 Analyzing item attributes..."):
        result = run_agent(item)

        # Check if LLM failed
        if not result.get('success', True):
            st.error(f"❌ **LLM Error**: {result.get('error', 'Unknown error occurred')}")
            st.warning("⚠️ **The system requires LLM reasoning to provide recommendations.** Please try again or check the API configuration.")
            # Don't update session state when there's an error
        else:
            st.session_state.last_result = result
            st.session_state.last_item = item

            # Add to audit log only on success
            st.session_state.audit_log.insert(0, {
                'item_id': item_id,
                'product': product_name[:20],
                'ai_zone': result['zone'],
                'final_zone': result['zone'],
                'overridden': False,
                'timestamp': datetime.now().strftime("%H:%M:%S"),
                'confidence': result['confidence'],
                'mandatory': result['mandatory']
            })

# ──────────────────────────────────────────────────────────────────────────
# COLUMN 2: AI RECOMMENDATION
# ──────────────────────────────────────────────────────────────────────────

with col2:
    st.markdown("""
    <div class="card">
        <div class="card-header">🤖 AI Recommendation</div>
    """, unsafe_allow_html=True)
    
    if st.session_state.last_result:
        r = st.session_state.last_result
        
        # Zone Display
        zone_class = "mandatory" if r['mandatory'] else ""
        st.markdown(f"""
        <div class="zone-display {zone_class}">
            <div class="zone-label">Recommended Zone</div>
            <div class="zone-code">ZONE {r['zone']}</div>
            <div class="zone-name">{r['zone_name']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Badges
        conf_class = f"badge-{r['confidence']}"
        backend_info = r.get('llm_backend', 'Unknown')
        st.markdown(f"""
        <div style="text-align: center; margin: 1rem 0;">
            <span class="badge {conf_class}">⚡ {r['confidence'].upper()} CONFIDENCE</span>
            <span class="badge badge-time">🕐 {r['decision_time']}s</span>
            {"<span class='badge badge-mandatory'>🔒 SAFETY RULE</span>" if r['mandatory'] else ""}
            <span class="badge" style="background: #667eea; color: white;">🤖 {backend_info}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Zone Details
        zd = r['zone_details']
        st.markdown(f"""
        <div class="zone-detail">
            <div class="zone-detail-item"><span>Rack Type:</span><span>{zd['rack_type']}</span></div>
            <div class="zone-detail-item"><span>Max Weight:</span><span>{zd['max_weight']}kg</span></div>
            <div class="zone-detail-item"><span>Temperature:</span><span>{zd['temp_range']}</span></div>
            <div class="zone-detail-item"><span>Dispatch Distance:</span><span>{zd['dispatch_distance']}m</span></div>
            <div class="zone-detail-item"><span>Equipment:</span><span>{zd['equipment']}</span></div>
        </div>
        """, unsafe_allow_html=True)
        
        # Reasoning
        st.markdown(f"""
        <div style="font-weight: 600; margin-top: 1.2rem; color: #1e3c72;">🧠 Decision Reasoning</div>
        <div class="reasoning-box">{r['reasoning']}</div>
        """, unsafe_allow_html=True)
        
    else:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; color: #999;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📋</div>
            <div style="font-size: 1.1rem;">Enter item details and click</div>
            <div style="font-size: 1.1rem; font-weight: 600;">"GET RECOMMENDATION"</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────
# COLUMN 3: SAFETY VALIDATION
# ──────────────────────────────────────────────────────────────────────────

with col3:
    st.markdown("""
    <div class="card">
        <div class="card-header">🛡️ Safety Validation</div>
    """, unsafe_allow_html=True)

    if st.session_state.last_result:
        r = st.session_state.last_result
        
        # Safety Checks
        for key, check in r['safety_checks'].items():
            icon = "✅" if check['status'] else "⚠️"
            status_class = "passed" if check['status'] else "warning"
            label = key.replace('_', ' ').title()
            
            st.markdown(f"""
            <div class="safety-item {status_class}">
                <span class="icon">{icon}</span>
                <div class="text">
                    <div class="label">{label}</div>
                    <div class="detail">{check['message']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Rejected Zones
        if r['rejected_zones']:
            st.markdown("<div style='font-weight: 600; margin-top: 1.2rem; color: #dc3545;'>❌ Rejected Zones</div>", unsafe_allow_html=True)
            
            for rej in r['rejected_zones'][:4]:
                st.markdown(f"""
                <div class="rejected-zone">
                    <span class="zone-id">Zone {rej['zone']}</span>: 
                    <span class="reason">{rej['reason']}</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; color: #999;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">🛡️</div>
            <div style="font-size: 1.1rem;">Safety validation results</div>
            <div style="font-size: 1.1rem;">will appear here</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# HUMAN OVERRIDE SECTION
# ============================================================================

if st.session_state.last_result:
    st.markdown("""
    <div class="override-section">
        <h3>👤 Human Override (Optional)</h3>
    </div>
    """, unsafe_allow_html=True)
    
    ov_col1, ov_col2, ov_col3 = st.columns([1, 2, 1])
    
    with ov_col1:
        override_zone = st.selectbox(
            "Select Zone",
            list(ZONES.keys()),
            format_func=lambda x: f"Zone {x} - {ZONES[x]['name']}",
            key="override_select"
        )
    
    with ov_col2:
        override_reason = st.text_input(
            "Override Reason",
            placeholder="e.g., Zone C at capacity, supervisor approved Zone A",
            key="override_reason"
        )
    
    with ov_col3:
        st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)
        if st.button("✏️ APPLY OVERRIDE", key="apply_override"):
            if st.session_state.audit_log:
                st.session_state.audit_log[0]['final_zone'] = override_zone
                st.session_state.audit_log[0]['overridden'] = True
                st.session_state.audit_log[0]['override_reason'] = override_reason
            st.success(f"✅ Override applied → Zone {override_zone}")
            st.balloons()

# ============================================================================
# AUDIT LOG
# ============================================================================

st.markdown("<div style='height: 2rem'></div>", unsafe_allow_html=True)
st.markdown("### 📜 Recent Decisions (Audit Trail)")

if st.session_state.audit_log:
    # Header
    cols = st.columns([1.5, 2, 1, 1, 1, 1])
    cols[0].markdown("**Item ID**")
    cols[1].markdown("**Product**")
    cols[2].markdown("**AI Zone**")
    cols[3].markdown("**Final**")
    cols[4].markdown("**Override**")
    cols[5].markdown("**Time**")
    
    st.markdown("<hr style='margin: 0.5rem 0; border-color: #eee;'>", unsafe_allow_html=True)
    
    for log in st.session_state.audit_log[:5]:
        cols = st.columns([1.5, 2, 1, 1, 1, 1])
        cols[0].code(log['item_id'][:15], language=None)
        cols[1].write(log.get('product', 'N/A')[:18])
        cols[2].write(f"Zone {log['ai_zone']}")
        
        final_style = "color: #28a745; font-weight: 600;" if not log['overridden'] else "color: #ffc107; font-weight: 600;"
        cols[3].markdown(f"<span style='{final_style}'>Zone {log['final_zone']}</span>", unsafe_allow_html=True)
        
        cols[4].write("✅ Yes" if log['overridden'] else "—")
        cols[5].write(log['timestamp'])
else:
    st.info("📋 No decisions logged yet. Process your first item to see the audit trail.")
