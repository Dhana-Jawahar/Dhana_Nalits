import json
import random
import argparse
import sys

def load_question_bank(json_path):
    """Loads persistent JSON question bank and checks for parsing validity."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def filter_valid_questions(questions, allow_incomplete=False):
    """Filters questions, excluding incomplete/partial ones unless explicitly allowed."""
    if allow_incomplete:
        return questions
    valid_q = [q for q in questions if q.get("is_complete", True)]
    return valid_q

def generate_sample_paper(json_path, num_questions=10, mode="random", topics=None, allow_incomplete=False):
    """
    Generates a sample questionnaire paper based on criteria:
    - mode: 'random' (mix of topics) or 'topic' (specific topic filtering)
    - topics: List of topics to filter by if mode=='topic'
    """
    bank_data = load_question_bank(json_path)
    all_questions = bank_data.get("questions", [])
    
    # Check JSON validity & incomplete items
    valid_questions = filter_valid_questions(all_questions, allow_incomplete)
    
    print(f"Loaded {len(all_questions)} questions ({len(valid_questions)} validated complete questions).")
    
    selected_questions = []
    
    if mode == "topic" and topics:
        topics_lower = [t.lower() for t in topics]
        filtered_questions = [
            q for q in valid_questions 
            if q.get("topic", "").lower() in topics_lower
        ]
        print(f"Filtered {len(filtered_questions)} questions for topics: {topics}")
        
        if len(filtered_questions) == 0:
            print("Warning: No complete questions found for specified topics.")
            return None
            
        sample_size = min(num_questions, len(filtered_questions))
        selected_questions = random.sample(filtered_questions, sample_size)
        
    elif mode == "random":
        sample_size = min(num_questions, len(valid_questions))
        selected_questions = random.sample(valid_questions, sample_size)
        
    else:
        print(f"Unknown mode '{mode}' or missing topics.")
        return None

    # Construct output paper structure
    sample_paper = {
        "paper_title": f"Sample Questionnaire ({mode.capitalize()} Selection)",
        "generated_count": len(selected_questions),
        "topics_included": list(set(q.get("topic", "General") for q in selected_questions)),
        "questions": selected_questions
    }
    
    return sample_paper

def export_paper_formats(paper_data, output_json_path):
    """Saves generated paper as JSON and printable TXT format."""
    # Export JSON
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(paper_data, f, indent=2, ensure_ascii=False)
    print(f"Saved generated sample paper to: {output_json_path}")
    
    # Export printable text version
    txt_path = output_json_path.rsplit('.', 1)[0] + ".txt"
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(f"=== {paper_data['paper_title']} ===\n")
        f.write(f"Total Questions: {paper_data['generated_count']}\n")
        f.write(f"Topics: {', '.join(paper_data['topics_included'])}\n\n")
        f.write("="*40 + "\n\n")
        
        for idx, q in enumerate(paper_data['questions'], start=1):
            f.write(f"Q{idx}. [{q.get('topic', 'General')}] {q['question_text']}\n")
            if q.get("options"):
                for opt in q["options"]:
                    f.write(f"   {opt}\n")
            f.write("\n")
            
        f.write("\n" + "="*40 + "\n")
        f.write("=== ANSWER KEY ===\n")
        for idx, q in enumerate(paper_data['questions'], start=1):
            f.write(f"Q{idx}: {q.get('correct_answer', 'N/A')}\n")
            
    print(f"Saved printable paper and answer key to: {txt_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sample Questionnaire Paper Generator")
    parser.add_argument("--json", type=str, required=True, help="Path to persistent question bank JSON")
    parser.add_argument("--num", type=int, default=10, help="Number of questions to select")
    parser.add_argument("--mode", type=str, choices=["random", "topic"], default="random", help="Selection mode: 'random' or 'topic'")
    parser.add_argument("--topics", nargs="+", help="Topic names to filter by (when --mode topic)")
    parser.add_argument("--output", type=str, default="sample_paper.json", help="Output path for sample paper JSON")
    parser.add_argument("--include_incomplete", action="store_true", help="Include questions marked as incomplete/partial")
    
    args = parser.parse_args()
    
    paper = generate_sample_paper(
        json_path=args.json,
        num_questions=args.num,
        mode=args.mode,
        topics=args.topics,
        allow_incomplete=args.include_incomplete
    )
    
    if paper:
        export_paper_formats(paper, args.output)
