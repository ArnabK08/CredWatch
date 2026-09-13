import subprocess
import sys
import os

BASE = os.path.dirname(os.path.abspath(__file__))

def run(script_path, label):
    print("\n" + "="*60)
    print("  STEP: " + label)
    print("  Script: " + script_path)
    print("="*60)
    result = subprocess.run([sys.executable, script_path], capture_output=False, cwd=BASE)
    if result.returncode != 0:
        print("\n[ERROR] Step '" + label + "' failed with exit code " + str(result.returncode))
        sys.exit(result.returncode)
    print("[OK] " + label + " complete.")

if __name__ == "__main__":
    steps = [
        ("data/raw/generate_data.py",              "1. Generate Synthetic Data"),
        ("sql/02_load_data.py",                    "2. Load Data into SQLite"),
        ("run_sql_queries.py",                     "3. Execute SQL Risk Queries"),
        ("credit_risk_model/feature_engineering.py", "4. Feature Engineering"),
        ("credit_risk_model/train_model.py",        "5. Train Credit Risk Model"),
        ("rules_engine/rules_engine.py",            "6. Run AML Rules Engine"),
        ("dashboard/prepare_dashboard_data.py",     "7. Prepare Dashboard Data"),
    ]
    for script, label in steps:
        run(os.path.join(BASE, script), label)
    
    print("\n" + "="*60)
    print("  ALL PIPELINE STEPS COMPLETE!")
    print("  Launch the Streamlit dashboard with:")
    print("    streamlit run streamlit_app.py")
    print("="*60 + "\n")
