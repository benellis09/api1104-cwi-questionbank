#!/usr/bin/env python3
"""
API 1104 CWI Question Generator - Batch Version
Generates 800 practice questions split into 8 batches of 100 questions each
Distribution per batch: 80 MCQ, 10 Matching, 10 Fill-in-the-Blank
"""

import csv
import json
from datetime import datetime
from typing import List, Dict

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
]

FILLIN_BLANKS = [
    ("A discontinuity formed by entrapment of flux between passes is called _____.", "slag inclusion"),
    ("The _____ is the area of base metal altered metallurgically by welding heat.", "heat-affected zone or HAZ"),
    ("Rapid cooling of steel typically produces _____ microstructure with high hardness.", "martensite"),
    ("A _____ is prepared by baking electrodes at elevated temperature to remove absorbed moisture.", "electrode oven or kiln"),
    ("The _____ specifies all essential and non-essential variables for weld production.", "welding procedure specification or WPS"),
    ("Groove _____ is the angle between the prepared joint faces.", "angle"),
    ("_____ is the perpendicular distance from the chord of a fillet weld to the hypotenuse.", "Throat"),
    ("The _____ is the maximum metal loss expected to occur during service life.", "corrosion allowance"),
    ("Incomplete fusion between the weld and base metal is called _____.", "lack of fusion"),
    ("_____ testing uses high-frequency sound waves to detect internal discontinuities.", "Ultrasonic"),
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
            "topic": "Welding terminology",
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

def write_batch_csv(batch_num: int, questions: List[Dict]):
    """Write questions to batch CSV file"""
    fieldnames = [
        "id", "type", "topic", "difficulty", "stem", "choices",
        "correct_answer", "explanation", "tags", "source_reference",
        "created_by", "created_at", "reviewer", "reviewer_notes"
    ]
    
    filename = f"csv/questions_batch_{batch_num:02d}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(questions)
    
    print(f"✓ Batch {batch_num:02d}: {len(questions)} questions → {filename}")

def main():
    """Generate 8 batches of 100 questions each (640 MCQ, 80 Matching, 80 Fill-in)"""
    
    print("Generating 8 batches of 100 questions each (800 total)")
    print("=" * 70)
    
    # Each batch: 80 MCQ + 10 Matching + 10 Fill-in
    mcq_per_batch = 80
    matching_per_batch = 10
    fillin_per_batch = 10
    
    for batch_num in range(1, 9):
        batch_questions = []
        
        # MCQ questions for this batch
        start_mcq_id = (batch_num - 1) * mcq_per_batch + 1
        mcq_questions = generate_mcq(start_mcq_id, mcq_per_batch)
        batch_questions.extend(mcq_questions)
        
        # Matching questions for this batch
        start_matching_id = 640 + (batch_num - 1) * matching_per_batch + 1
        matching_questions = generate_matching(start_matching_id, matching_per_batch)
        batch_questions.extend(matching_questions)
        
        # Fill-in questions for this batch
        start_fillin_id = 720 + (batch_num - 1) * fillin_per_batch + 1
        fillin_questions = generate_fillin(start_fillin_id, fillin_per_batch)
        batch_questions.extend(fillin_questions)
        
        # Write batch to CSV
        write_batch_csv(batch_num, batch_questions)
    
    print("=" * 70)
    print(f"\n✓ Generated 8 batches (800 total questions)")
    print(f"  • Batches 01-08 each contain:")
    print(f"    - 80 MCQ (Q001-Q640 across all batches)")
    print(f"    - 10 Matching (Q641-Q720 across all batches)")
    print(f"    - 10 Fill-in (Q721-Q800 across all batches)")
    print(f"\n  • Output: csv/questions_batch_01.csv through csv/questions_batch_08.csv")

if __name__ == "__main__":
    main()
