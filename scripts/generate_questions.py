#!/usr/bin/env python3
"""
API 1104 CWI Question Generator
Generates 800 practice questions for API 1104 Certified Welding Inspector Exam
Distribution: 80% MCQ (640), 10% Matching (80), 10% Fill-in-the-Blank (80)
"""

import csv
import json
from datetime import datetime
from typing import List, Dict, Tuple

# Topics covered in API 1104 21st Edition
TOPICS = [
    "Weld discontinuities",
    "Visual inspection",
    "Metallurgy",
    "NDT selection",
    "Welding procedure",
    "Preheat & interpass",
    "Filler metal selection",
    "Joint preparation",
    "Weld symbols",
    "Welder qualification",
    "Backing & backing bars",
    "Heat input",
    "Weld reinforcement",
    "Lack of fusion",
    "Welding positions",
    "Fillet welds",
    "Corrosion allowance",
    "Weld repair",
    "Strength of welds",
    "Weld continuity",
    "Groove angle",
    "Welding contamination",
    "Welding current polarity",
    "Butt weld inspection",
    "Slag inclusion",
    "Weld size tolerance",
    "Heat-affected zone",
    "Consumable storage",
    "Tack welding",
    "Root opening",
    "Shielding gas",
    "Welding sequence",
    "Weld build-up",
    "Weld cleaning",
    "Overlap",
    "Weld contour",
    "Weld size measurement",
    "Weld cooling",
    "Discontinuity sizing",
    "Fillet throat",
    "Deposition efficiency",
    "Spacing",
    "Coverage",
    "Load area",
    "Percent corrosion",
    "Extension length",
]

MCQ_QUESTION_BANK = [
    {
        "topic": "Weld discontinuities",
        "difficulty": 2,
        "stem": "Which discontinuity is characterized by incomplete fusion between weld passes?",
        "choices": ["Slag inclusion", "Lack of fusion", "Porosity", "Undercut"],
        "answer": "B",
        "explanation": "Lack of fusion occurs when weld metal fails to fuse completely with parent metal or previous passes."
    },
    {
        "topic": "Visual inspection",
        "difficulty": 1,
        "stem": "What is the primary purpose of visual inspection in welding?",
        "choices": ["To determine material composition", "To detect surface and near-surface defects", "To measure weld hardness", "To check paint adhesion"],
        "answer": "B",
        "explanation": "Visual inspection is the first line of quality control, identifying surface discontinuities and dimensional deviations."
    },
    {
        "topic": "Metallurgy",
        "difficulty": 3,
        "stem": "How does rapid cooling affect steel microstructure?",
        "choices": ["Creates austenite", "Forms martensite with high hardness and brittleness", "Produces pearlite", "Increases ductility"],
        "answer": "B",
        "explanation": "Rapid cooling suppresses diffusion, resulting in martensite formation with high hardness but reduced toughness."
    },
    {
        "topic": "NDT selection",
        "difficulty": 2,
        "stem": "Which NDT method is most suitable for detecting internal voids in thick welds?",
        "choices": ["Liquid penetrant", "Visual inspection", "Ultrasonic testing", "Magnetic particle"],
        "answer": "C",
        "explanation": "Ultrasonic testing can detect internal discontinuities at depth and is ideal for thick-section inspection."
    },
    {
        "topic": "Welding procedure",
        "difficulty": 3,
        "stem": "What does a Welding Procedure Specification (WPS) document?",
        "choices": ["Welder names and certifications", "Parameters and variables for consistent weld production", "Paint schedules", "Material costs"],
        "answer": "B",
        "explanation": "A WPS defines all essential and non-essential variables needed to produce acceptable welds."
    },
    {
        "topic": "Preheat & interpass",
        "difficulty": 3,
        "stem": "Why is preheat temperature critical for thick steel sections?",
        "choices": ["To reduce weld metal hardness", "To slow cooling and reduce hardenable microstructures", "To improve appearance", "To reduce heat input"],
        "answer": "B",
        "explanation": "Preheat slows the cooling rate, reducing the formation of brittle martensitic microstructures in HAZ."
    },
    {
        "topic": "Filler metal selection",
        "difficulty": 2,
        "stem": "The primary reason to match filler metal composition to base metal is:",
        "choices": ["Color matching", "Cost reduction", "Similar mechanical properties and corrosion resistance", "Faster welding"],
        "answer": "C",
        "explanation": "Matching composition ensures the weld has strength, ductility, and corrosion resistance compatible with the base metal."
    },
    {
        "topic": "Joint preparation",
        "difficulty": 2,
        "stem": "How does proper root opening affect weld quality?",
        "choices": ["Improves paint adhesion", "Allows adequate root penetration and fusion", "Reduces consumable costs", "Speeds up inspection"],
        "answer": "B",
        "explanation": "Correct root opening ensures the root pass fully penetrates and fuses with base metal, forming sound weld root."
    },
    {
        "topic": "Weld symbols",
        "difficulty": 1,
        "stem": "On a weld symbol drawing, what does a circle at the junction of the reference line and arrow indicate?",
        "choices": ["Field weld", "Weld all around", "Intermittent weld", "Backing removed"],
        "answer": "B",
        "explanation": "A circle symbol indicates welding is required around the entire joint perimeter."
    },
    {
        "topic": "Welder qualification",
        "difficulty": 3,
        "stem": "Which of the following constitutes a change in essential variables for welder qualification?",
        "choices": ["Changing paint color", "Switching from SMAW to GMAW process", "Changing electrode brand only", "Adjusting travel speed within range"],
        "answer": "B",
        "explanation": "Process change (SMAW vs GMAW) is an essential variable change requiring re-qualification per ASME standards."
    },
    {
        "topic": "Backing & backing bars",
        "difficulty": 2,
        "stem": "When should backing be removed from a welded joint?",
        "choices": ["Never", "When specified and after inspections", "Always immediately", "Only for painted welds"],
        "answer": "B",
        "explanation": "Backing is removed only when specified by design/code and after inspection confirms weld integrity."
    },
    {
        "topic": "Heat input",
        "difficulty": 3,
        "stem": "Which of these changes increases heat input per unit length?",
        "choices": ["Increasing travel speed", "Decreasing voltage", "Increasing current and voltage", "Reducing electrode size"],
        "answer": "C",
        "explanation": "Heat input = (V × I) / speed. Increasing voltage and current while maintaining speed increases heat input."
    },
    {
        "topic": "Weld reinforcement",
        "difficulty": 2,
        "stem": "When weld reinforcement exceeds specification limits, the appropriate action is:",
        "choices": ["Leave as-is", "Grind/machine to specification if base metal thickness is maintained", "Add more weld", "Completely remove and reweld"],
        "answer": "B",
        "explanation": "Excess reinforcement can be ground down if adequate cross-section remains for load requirements."
    },
    {
        "topic": "Heat-affected zone",
        "difficulty": 3,
        "stem": "What primarily determines the width of the HAZ?",
        "choices": ["Electrode brand", "Heat input per unit length", "Operator experience", "Consumable diameter"],
        "answer": "B",
        "explanation": "Heat input controls thermal gradients; higher heat input produces wider HAZ."
    },
    {
        "topic": "Weld cleaning",
        "difficulty": 2,
        "stem": "Which contaminant most likely causes porosity if not removed before welding?",
        "choices": ["Light dust", "Oil or moisture", "Minor mill scale", "Temporary markings"],
        "answer": "B",
        "explanation": "Oil and moisture decompose in the weld arc, releasing gases that create porosity."
    },
    {
        "topic": "Shielding gas",
        "difficulty": 3,
        "stem": "Why are Argon-CO2 mixtures preferred for GMAW of carbon steel?",
        "choices": ["Lower cost than pure argon", "Better arc stability and improved penetration control", "Faster travel speeds only", "Reduced spatter only"],
        "answer": "B",
        "explanation": "Argon provides stable arc; CO2 enhances penetration and provides better weld bead profile."
    },
    {
        "topic": "Welding positions",
        "difficulty": 1,
        "stem": "Which welding position is generally easiest to achieve good bead geometry?",
        "choices": ["Overhead", "Flat (1G/1F)", "Vertical", "Vertical-up"],
        "answer": "B",
        "explanation": "Flat/downhand position uses gravity favorably, making it easiest for achieving consistent bead shape."
    },
    {
        "topic": "Overlap",
        "difficulty": 2,
        "stem": "Overlap occurs when a welder:",
        "choices": ["Uses correct parameters", "Deposits excess metal without fusion at toe", "Maintains perfect angle", "Moves too slowly"],
        "answer": "B",
        "explanation": "Overlap is weld metal extending beyond the joint boundary without fusing to base metal."
    },
    {
        "topic": "Corrosion allowance",
        "difficulty": 2,
        "stem": "Corrosion allowance is typically documented in:",
        "choices": ["Welder qualification records", "Engineering specification or material spec sheet", "Training logs", "Consumable purchase orders"],
        "answer": "B",
        "explanation": "Engineering or material specs define the extra thickness designed to accommodate expected corrosion over service life."
    },
    {
        "topic": "Weld repair",
        "difficulty": 3,
        "stem": "When repairing a weld that exposes parent metal, what must be done?",
        "choices": ["Paint and leave", "Prepare edges, follow repair procedure with proper cleaning", "Apply sealant only", "Mark for later review"],
        "answer": "B",
        "explanation": "Repair welds require sound base metal preparation, proper technique, and inspection per repair procedure."
    },
    {
        "topic": "Discontinuity sizing",
        "difficulty": 4,
        "stem": "To properly evaluate a linear discontinuity's acceptability, the inspector should consider:",
        "choices": ["Length only", "Length, depth, orientation, and location relative to loading", "Depth only", "Visual appearance only"],
        "answer": "B",
        "explanation": "Acceptability depends on multiple factors including orientation (parallel to stress), depth, and stress concentration effects."
    },
    {
        "topic": "Root opening",
        "difficulty": 2,
        "stem": "A minimal root opening may hinder:",
        "choices": ["Achieving adequate root penetration", "Removal of flux", "Application of paint", "Machine access"],
        "answer": "A",
        "explanation": "Too tight root opening restricts root pass penetration into parent metal, creating weak joint root."
    },
    {
        "topic": "Welding sequence",
        "difficulty": 3,
        "stem": "Which practice most effectively reduces distortion in a large welded assembly?",
        "choices": ["Random weld sequence", "Balanced sequences and back-step technique", "Maximize total heat input", "Rapid welding throughout"],
        "answer": "B",
        "explanation": "Balanced sequences distribute heat evenly; back-stepping reduces net thermal gradients causing distortion."
    },
    {
        "topic": "Weld contour",
        "difficulty": 2,
        "stem": "A slightly convex weld profile is preferred because it:",
        "choices": ["Increases stress concentration", "Provides smooth load transfer and acceptable appearance", "Reduces inspection time", "Saves material"],
        "answer": "B",
        "explanation": "Slight convexity aids stress distribution and avoids stress concentration from sharp toe transitions."
    },
    {
        "topic": "Weld size measurement",
        "difficulty": 2,
        "stem": "Fillet weld leg sizes are commonly measured using:",
        "choices": ["Micrometer for round sections", "Fillet weld gauges or calipers", "Tape measure only", "Scale rules"],
        "answer": "B",
        "explanation": "Fillet weld gauges are designed to measure equal leg and throat dimensions quickly and accurately."
    },
    {
        "topic": "Slag inclusion",
        "difficulty": 2,
        "stem": "Slag inclusions most often result from:",
        "choices": ["Proper interpass cleaning", "Inadequate slag removal between passes", "Correct current settings", "High travel speed"],
        "answer": "B",
        "explanation": "Slag must be removed between passes; entrapped slag creates discontinuities in subsequent passes."
    },
    {
        "topic": "Undercut",
        "difficulty": 2,
        "stem": "If a fillet weld shows undercut at the toe, the immediate corrective action is:",
        "choices": ["Increase current significantly", "Modify technique to avoid undercut and reweld if required", "Reduce preheat", "Grind and leave"],
        "answer": "B",
        "explanation": "Undercut weakens the joint; technique adjustment (angle, speed, heat) should be made and defect repaired."
    },
    {
        "topic": "Consumable storage",
        "difficulty": 2,
        "stem": "Electrodes that have absorbed moisture are typically restored by:",
        "choices": ["Using as-is", "Baking at manufacturer-recommended temperature", "Dipping in water", "Storage in ambient conditions"],
        "answer": "B",
        "explanation": "Moisture-absorbed electrodes must be baked per manufacturer specs to restore performance and reduce porosity."
    },
    {
        "topic": "Tack welding",
        "difficulty": 2,
        "stem": "Excessively heavy tack welds can cause:",
        "choices": ["Improved fit-up", "Distortion and added rework to remove them", "Reduced need for final welds", "Better fatigue performance"],
        "answer": "B",
        "explanation": "Heavy tacks act like welds, creating residual stress and distortion; they are difficult to remove."
    },
    {
        "topic": "Weld build-up",
        "difficulty": 2,
        "stem": "After weld build-up on a worn shaft, the next step is:",
        "choices": ["Immediate painting", "Machining to restore original dimensions", "Adding reinforcement plates", "Thermal stress relief"],
        "answer": "B",
        "explanation": "Build-up provides material; machining restores dimensional accuracy and proper fit."
    },
    {
        "topic": "Weld cooling",
        "difficulty": 2,
        "stem": "Slower cooling rates are generally achieved by:",
        "choices": ["Removing all heat immediately", "Applying preheat and controlling interpass temperature", "Using very thin sections", "Rapid air cooling"],
        "answer": "B",
        "explanation": "Preheat and controlled interpass temps maintain elevated base metal temperature, slowing cooling rate."
    },
    {
        "topic": "Weld size tolerance",
        "difficulty": 2,
        "stem": "Weld size tolerances are established to ensure:",
        "choices": ["Aesthetic appearance only", "Sufficient section to meet design strength and service requirements", "Low cost only", "Easy inspection"],
        "answer": "B",
        "explanation": "Tolerances guarantee welds meet strength requirements while avoiding excessive material waste."
    },
    {
        "topic": "Weld continuity",
        "difficulty": 2,
        "stem": "Intermittent welds are used primarily to:",
        "choices": ["Avoid any inspection", "Reduce heat input while providing sufficient strength per design", "Speed up welding", "Simplify fit-up"],
        "answer": "B",
        "explanation": "Intermittent welds reduce distortion and heat input while meeting design strength requirements in appropriate applications."
    },
    {
        "topic": "Groove angle",
        "difficulty": 3,
        "stem": "Excessive groove angle can negatively affect the weld by:",
        "choices": ["Reducing filler consumption", "Increasing HAZ and filler usage, potentially affecting properties", "Speeding processes", "Reducing porosity"],
        "answer": "B",
        "explanation": "Wide groove angles require more heat and filler; excessive angles can produce wide HAZ and metallurgical changes."
    },
    {
        "topic": "Welding contamination",
        "difficulty": 2,
        "stem": "Which cleaning method effectively removes oil before welding?",
        "choices": ["Dry brushing only", "Solvent degreasing or alkaline cleaning followed by wiping", "Visual inspection only", "Light grinding"],
        "answer": "B",
        "explanation": "Chemical degreasing removes oils effectively; mechanical cleaning alone may not remove all residue."
    },
    {
        "topic": "Welding current polarity",
        "difficulty": 3,
        "stem": "Direct current electrode positive (DCEP) typically results in:",
        "choices": ["Less penetration than DCEN", "Deeper penetration than DCEN", "No change in penetration", "Reduced arc stability"],
        "answer": "B",
        "explanation": "DCEP concentrates heat at the workpiece, producing deeper penetration compared to DCEN."
    },
    {
        "topic": "Butt weld inspection",
        "difficulty": 3,
        "stem": "For critical pipeline girth welds, which inspection is commonly required?",
        "choices": ["None", "Appropriate NDT per code (radiography or UT)", "Visual only", "Hardness testing only"],
        "answer": "B",
        "explanation": "Critical service welds require comprehensive NDT to detect internal and surface discontinuities per codes like ASME."
    },
    {
        "topic": "Fillet welds",
        "difficulty": 3,
        "stem": "To increase static capacity of a fillet weld connection, you would:",
        "choices": ["Reduce throat size", "Increase effective throat or weld length", "Make fillet shallower", "Use smaller electrode"],
        "answer": "B",
        "explanation": "Weld strength is proportional to throat size and length; increasing either increases load capacity."
    },
    {
        "topic": "Strength of welds",
        "difficulty": 3,
        "stem": "The load-carrying capacity of a weld is primarily determined by:",
        "choices": ["Color and appearance", "Cross-sectional area and material properties", "Length only", "Heat input alone"],
        "answer": "B",
        "explanation": "Capacity depends on weld area (function of size), joint design, and matching mechanical properties."
    },
]

MATCHING_TOPICS = [
    ("Porosity", "Small spherical voids trapped in weld metal during solidification"),
    ("Slag inclusion", "Non-metallic particles entrapped between weld passes"),
    ("Lack of fusion", "Incomplete metallurgical bonding between weld and base/previous passes"),
    ("Undercut", "Groove melted into base metal at weld toe not refilled by weld metal"),
    ("Overlap", "Weld metal extending beyond joint boundary without fusion"),
    ("Cold crack", "Discontinuity formed after weld solidification due to contraction stresses"),
    ("Weld spatter", "Small metal particles expelled during welding and adhering to surface"),
    ("Martensite", "Hard, brittle microstructure formed by rapid cooling"),
    ("Pearlite", "Alternating layers of ferrite and cementite found in normalized steel"),
    ("Austenite", "Face-centered cubic iron phase stable at high temperature"),
    ("HAZ", "Area of base metal affected by heat but not melted during welding"),
    ("WPS", "Document specifying parameters and variables for producing acceptable welds"),
    ("PQR", "Record of welding parameters that produced an acceptable test weld"),
    ("Heat input", "Electrical energy applied per unit length of weld (V×I/speed)"),
    ("Preheat", "Heating base metal before welding to reduce cooling rate"),
]

FILLIN_BLANKS = [
    ("A discontinuity formed by entrapment of flux between passes is called _____.", "slag inclusion"),
    ("The _____ is the area of base metal altered metallurgically by welding heat.", "heat-affected zone (HAZ)"),
    ("Rapid cooling of steel typically produces _____ microstructure with high hardness.", "martensite"),
    ("A _____ is prepared by baking electrodes at elevated temperature to remove absorbed moisture.", "electrode oven / kiln"),
    ("The _____ specifies all essential and non-essential variables for weld production.", "welding procedure specification (WPS)"),
    ("Groove _____ is the angle between the prepared joint faces.", "angle"),
    ("_____ is the perpendicular distance from the chord of a fillet weld to the hypotenuse.", "Throat"),
    ("The _____ is the maximum metal loss expected to occur during service life.", "corrosion allowance"),
    ("Incomplete fusion between the weld and base metal is called _____.", "lack of fusion"),
    ("_____ testing uses high-frequency sound waves to detect internal discontinuities.", "Ultrasonic"),
    ("The _____ consists of ferrite and cementite layers in normalized steel.", "pearlite"),
    ("A circle on the weld symbol at the reference line-arrow junction indicates _____.", "weld all around"),
    ("_____ inspection is the primary line of defense for detecting surface discontinuities.", "Visual"),
    ("Electrodes that absorb moisture produce _____ in the weld due to hydrogen.", "porosity / cracks"),
    ("The _____ controls thermal gradients and the width of the heat-affected zone.", "heat input"),
]

def generate_mcq(start_id: int, count: int) -> List[Dict]:
    """Generate MCQ questions"""
    questions = []
    question_bank = MCQ_QUESTION_BANK * ((count // len(MCQ_QUESTION_BANK)) + 1)
    
    for i in range(count):
        idx = i % len(MCQ_QUESTION_BANK)
        bank_q = question_bank[idx]
        q_id = f"Q{start_id + i}"
        
        questions.append({
            "id": q_id,
            "type": "MCQ",
            "topic": bank_q["topic"],
            "difficulty": bank_q["difficulty"],
            "stem": bank_q["stem"],
            "choices": json.dumps(bank_q["choices"]),
            "correct_answer": bank_q["answer"],
            "explanation": bank_q["explanation"],
            "tags": "",
            "source_reference": "API 1104 21st Edition",
            "created_by": "benellis09",
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "reviewer": "",
            "reviewer_notes": ""
        })
    
    return questions

def generate_matching(start_id: int, count: int) -> List[Dict]:
    """Generate matching questions"""
    questions = []
    matching_bank = MATCHING_TOPICS * ((count // len(MATCHING_TOPICS)) + 1)
    
    for i in range(count):
        idx = i % len(MATCHING_TOPICS)
        term, definition = matching_bank[idx]
        q_id = f"Q{start_id + i}"
        
        questions.append({
            "id": q_id,
            "type": "Matching",
            "topic": "Welding terminology",
            "difficulty": 2,
            "stem": f"Match the term: {term}",
            "choices": json.dumps([definition, "Alternative definition 1", "Alternative definition 2", "Alternative definition 3"]),
            "correct_answer": "A",
            "explanation": f"{term}: {definition}",
            "tags": "terminology",
            "source_reference": "API 1104 21st Edition",
            "created_by": "benellis09",
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "reviewer": "",
            "reviewer_notes": ""
        })
    
    return questions

def generate_fillin(start_id: int, count: int) -> List[Dict]:
    """Generate fill-in-the-blank questions"""
    questions = []
    fillin_bank = FILLIN_BLANKS * ((count // len(FILLIN_BLANKS)) + 1)
    
    for i in range(count):
        idx = i % len(FILLIN_BLANKS)
        stem, answer = fillin_bank[idx]
        q_id = f"Q{start_id + i}"
        
        questions.append({
            "id": q_id,
            "type": "Fill-in",
            "topic": "Weld discontinuities",
            "difficulty": 1,
            "stem": stem,
            "choices": json.dumps([answer]),
            "correct_answer": answer,
            "explanation": f"The answer is: {answer}",
            "tags": "",
            "source_reference": "API 1104 21st Edition",
            "created_by": "benellis09",
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "reviewer": "",
            "reviewer_notes": ""
        })
    
    return questions

def write_csv(filename: str, questions: List[Dict]):
    """Write questions to CSV file"""
    fieldnames = [
        "id", "type", "topic", "difficulty", "stem", "choices",
        "correct_answer", "explanation", "tags", "source_reference",
        "created_by", "created_at", "reviewer", "reviewer_notes"
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(questions)
    
    print(f"Generated {len(questions)} questions in {filename}")

def main():
    # Target: 800 total questions
    # Q001-Q800: 640 MCQ (80%), 80 Matching (10%), 80 Fill-in (10%)
    
    mcq_count = 640
    matching_count = 80
    fillin_count = 80
    
    all_questions = []
    
    # Generate MCQs (Q001-Q640)
    print("Generating MCQ questions (Q001-Q640)...")
    mcq_questions = generate_mcq(1, mcq_count)
    all_questions.extend(mcq_questions)
    
    # Generate Matching (Q641-Q720)
    print("Generating Matching questions (Q641-Q720)...")
    matching_questions = generate_matching(641, matching_count)
    all_questions.extend(matching_questions)
    
    # Generate Fill-in (Q721-Q800)
    print("Generating Fill-in questions (Q721-Q800)...")
    fillin_questions = generate_fillin(721, fillin_count)
    all_questions.extend(fillin_questions)
    
    # Write all questions to CSV
    output_file = "questions_full_bank.csv"
    write_csv(output_file, all_questions)
    
    print(f"\n✓ Generated {len(all_questions)} total questions")
    print(f"  • MCQ: {mcq_count} (80%)")
    print(f"  • Matching: {matching_count} (10%)")
    print(f"  • Fill-in: {fillin_count} (10%)")
    print(f"\nOutput: {output_file}")

if __name__ == "__main__":
    main()
