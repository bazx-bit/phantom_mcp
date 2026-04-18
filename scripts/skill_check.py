import os
import sys

def check_skill(filepath):
    """Validates a single .md skill file."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    filename = os.path.basename(filepath)
    errors = []
    
    # Required Sections
    if not content.startswith("# "):
        errors.append("Missing H1 title (e.g., # 🔮 Aesthetic Auditor)")
    
    required_heads = ["## Prime Directive", "## Workflow", "## Scoring Rubric"]
    for head in required_heads:
        if head not in content:
            errors.append(f"Missing required section: {head}")
    
    # Tool References
    if "ghost_" not in content:
        errors.append("No reference to any 'ghost_' tools found.")
    
    # Length Check
    if len(content) < 500:
        errors.append("Skill prompt is too short (min 500 chars).")
    
    return errors

def main():
    skills_dir = os.path.join(os.path.dirname(__file__), "..", "engine", "src", "skills")
    if not os.path.exists(skills_dir):
        print(f"❌ Skills directory not found at {skills_dir}")
        sys.exit(1)
    
    files = [f for f in os.listdir(skills_dir) if f.endswith(".md")]
    print(f"👻 Validating {len(files)} Site-Ghost Skills...")
    print("-" * 40)
    
    all_passed = True
    for f in files:
        path = os.path.join(skills_dir, f)
        errors = check_skill(path)
        if errors:
            print(f"❌ {f}")
            for err in errors:
                print(f"    - {err}")
            all_passed = False
        else:
            print(f"✅ {f}")
    
    print("-" * 40)
    if all_passed:
        print("🎉 ALL SKILLS PASS PERFORMANCE GATE")
        sys.exit(0)
    else:
        print("🛑 SKILL QUALITY GATE FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()
