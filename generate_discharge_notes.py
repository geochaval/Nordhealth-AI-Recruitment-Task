import argparse
import json
import os
from typing import Dict, Any
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

def generate_discharge_note(data: Dict[str, Any]) -> str:
    # Extract relevant information from the consultation data
    patient = data["patient"]
    consultation = data["consultation"]
    clinical_notes = "\n".join(
        [note["note"].strip()  # Remove whitespace from individual notes
        for note in consultation["clinical_notes"] 
        if note["note"].strip()]  # Filter out empty/whitespace-only notes
    ) or "No clinical notes provided"  # Fallback if all notes are empty
        
    # Format treatments information
    treatments = []
    for category in ["procedures", "medicines", "prescriptions", "foods", "supplies"]:
        items = consultation["treatment_items"].get(category, [])
        if items:
            treatments.append(
                f"{category.capitalize()}: {', '.join(item['name'] for item in items)}"
            )
    
    # Create prompt template
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", """You are a veterinary assistant tasked with generating clear, professional discharge notes. Use ONLY the provided consultation information. Format in plain text without markdown. Respond with only the discharge note text—no JSON keys or commentary."""),
        ("human", """Patient Information
Name: {name}
Species: {species}
Breed: {breed}
Age: {age}
Weight: {weight}
Neutered: {neutered}

Consultation Details
Date: {date}
Reason: {reason}
Type: {type}

Clinical Notes
{clinical_notes}

Treatments
{treatments}

Using ONLY the provided consultation information, generate a concise discharge note summarizing the consultation, including: 
- Patient's condition
- Treatments/procedures performed. If no procedures were performed, say “No procedures were performed.” If no medications and prescriptions were given, say "No medications were given."
- Clear next steps and follow-up instructions (if any)""")
    ])

    # Calculate age
    dob = patient["date_of_birth"]
    age = f"{(datetime.strptime(consultation['date'], '%Y-%m-%d') - datetime.strptime(dob, '%Y-%m-%d')).days // 365} years" if dob else "Unknown"
    
    
    # Format prompt
    prompt = prompt_template.format_messages(
        name=patient["name"],
        species=patient["species"].split("(")[0].strip(),
        breed=patient["breed"],
        age=age,
        weight=patient["weight"],
        neutered=patient["neutered"],
        date=consultation["date"],
        reason=consultation["reason"],
        type=consultation["type"],
        clinical_notes=clinical_notes,
        treatments="\n".join(treatments) or "No treatments administered"
    )

    # Initialize LLM
    llm = ChatOpenAI(
        model_name="gpt-4o-mini",
        temperature=0.3,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Generate and return response
    response = llm.invoke(prompt)
    return response.content.strip()

def main():
    parser = argparse.ArgumentParser(description="Generate veterinary discharge notes from consultation data")
    parser.add_argument("input_json", help="Path to input JSON file(required)")
    args = parser.parse_args()

    # Check if file exists
    if not os.path.isfile(args.input_json):
        parser.error(f"File {args.input_json} does not exist")

    # Load consultation json
    try:
        with open(args.input_json, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        parser.error("Invalid JSON file")

    # Generate discharge note
    discharge_note = generate_discharge_note(data)
    
    # Output discharge note in json
    print(json.dumps({"discharge_note": discharge_note}, indent=2))

    # Create solution directory if it doesn't exist
    output_dir = "solution"
    os.makedirs(output_dir, exist_ok=True)

    i = args.input_json[-6]

    # Generate output filename
    output_path = os.path.join(output_dir, "discharge_note" + i + ".json")

    # Write to file
    with open(output_path, "w") as f:
        json.dump({"discharge_note": discharge_note}, f, indent=2)

if __name__ == "__main__":
    main()