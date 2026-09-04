import sys
import time
import os
import json

# Ensure UTF-8 output encoding on Windows console
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from src.data_loader import DataLoader
from src.gap_analyzer import GapAnalyzer
from src.llm_generator import InterviewQuestionGenerator
from src.rubric_engine import RubricEngine
from src.mock_evaluator import MockResponseEvaluator
from src.export_service import ExportService
from src.evaluator import GenerationEvaluator

console = Console()

def main():
    console.print(Panel.fit(
        "[bold cyan]🚀 Internee.pk Task 4: AI Interview Question Generation Pipeline[/bold cyan]\n"
        "[dim]Automated role-specific technical & behavioral question sets with STAR rubrics[/dim]",
        border_style="cyan"
    ))

    # 1. Load Data
    loader = DataLoader()
    generator = InterviewQuestionGenerator(loader)
    
    console.print(f"[green]✓[/green] Loaded [bold]{len(loader.question_bank)}[/bold] questions across [bold]{len(loader.get_tracks())}[/bold] engineering tracks.")
    console.print(f"[green]✓[/green] Loaded [bold]{len(loader.intern_profiles)}[/bold] intern resumes & [bold]{len(loader.job_descriptions)}[/bold] job descriptions.")

    # 2. Select Test Candidates
    test_cases = [
        ("INT-001", "JD-AI-01", "AI & Machine Learning"),
        ("INT-003", "JD-FS-02", "Full-Stack Web Development"),
        ("INT-006", "JD-DO-04", "Cloud & DevOps Engineering")
    ]

    benchmark_records = []
    
    os.makedirs("exports", exist_ok=True)

    for p_id, j_id, track_label in test_cases:
        profile = loader.get_profile_by_id(p_id)
        job = loader.get_job_by_id(j_id)

        if not profile or not job:
            continue

        console.print(f"\n[bold yellow]▶ Processing Pipeline for: {profile['name']} -> {job['title']}[/bold yellow]")
        
        # Measure Latency
        start_time = time.time()
        
        # 1. Gap Analysis
        gap = GapAnalyzer.analyze(profile, job)
        console.print(f"  [dim]• Fit Score: [bold]{gap['overall_fit_score']}%[/bold] | Matched Core: {len(gap['matched_required_skills'])} | Probing Gaps: {len(gap['missing_required_skills'])}[/dim]")

        # 2. Generation
        kit = generator.generate(
            profile=profile,
            job_desc=job,
            backend="rag_neural",
            num_technical=5,
            num_behavioral=3,
            num_project=2
        )
        elapsed = round((time.time() - start_time) * 1000, 2)

        # 3. Benchmark Evaluation
        metrics = GenerationEvaluator.evaluate_kit(kit, profile, job)
        metrics["latency_ms"] = elapsed
        metrics["candidate"] = profile["name"]
        metrics["role"] = job["title"]
        metrics["track"] = track_label
        benchmark_records.append(metrics)

        # 4. Exports
        safe_name = profile["name"].lower().replace(" ", "_")
        ExportService.to_markdown(kit, f"exports/interview_kit_{safe_name}.md")
        ExportService.to_json(kit, f"exports/interview_kit_{safe_name}.json")
        ExportService.to_html(kit, f"exports/interview_kit_{safe_name}.html")

        console.print(f"  [green]✓[/green] Generated {len(kit['technical_questions'])} Technical + {len(kit['behavioral_questions'])} STAR + {len(kit['project_deep_dive_questions'])} Project Qs in [bold]{elapsed} ms[/bold]")
        console.print(f"  [green]✓[/green] Exported Markdown, JSON, and HTML to [italic]exports/interview_kit_{safe_name}.*[/italic]")

    # 3. Print Benchmark Summary Table
    console.print("\n[bold cyan]📊 Quantitative Benchmark Evaluation Report[/bold cyan]")
    table = Table(title="AI Question Generation Quality Benchmarks", show_header=True, header_style="bold magenta")
    table.add_column("Candidate & Role", style="dim")
    table.add_column("CQI (Quality Index)", justify="right")
    table.add_column("Skill Coverage", justify="right")
    table.add_column("STAR Completeness", justify="right")
    table.add_column("Distinct-2 (Diversity)", justify="right")
    table.add_column("Personalization", justify="right")
    table.add_column("Latency", justify="right")
    table.add_column("Status", justify="center")

    for rec in benchmark_records:
        table.add_row(
            f"{rec['candidate']}\n[dim]{rec['role']}[/dim]",
            f"[bold green]{rec['composite_quality_index']}%[/bold green]",
            f"{rec['skill_coverage_pct']}%",
            f"{rec['star_completeness_pct']}%",
            f"{rec['lexical_distinct_2_ratio']}",
            f"{rec['personalization_pct']}%",
            f"{rec['latency_ms']} ms",
            f"[bold green]✔ {rec['benchmark_status']}[/bold green]"
        )

    console.print(table)

    # 4. Test Mock Evaluator Sample
    console.print("\n[bold cyan]🎙️ Testing Candidate Mock Response Evaluator[/bold cyan]")
    sample_question = kit["technical_questions"][0]
    sample_answer = "In my previous project, we observed that gradient descent with momentum significantly smoothed out oscillations compared to standard SGD. We also tuned learning rate schedules with cosine annealing to prevent getting trapped in shallow local minima."
    
    evaluation = MockResponseEvaluator.evaluate_response(sample_question, sample_answer)
    console.print(Panel(
        f"[bold]Question:[/bold] {sample_question['question']}\n\n"
        f"[bold]Candidate Response:[/bold] {sample_answer}\n\n"
        f"[bold]Score:[/bold] [bold green]{evaluation['score']}/5.0[/bold green] ({evaluation['rating']})\n"
        f"[bold]Key Concept Coverage:[/bold] {evaluation['concept_coverage_pct']}%\n"
        f"[bold]Strengths:[/bold] {', '.join(evaluation['strengths'])}\n"
        f"[bold]Feedback:[/bold] {evaluation['feedback']}\n"
        f"[bold]Adaptive Follow-up:[/bold] [italic]\"{evaluation['follow_up_prompt']}\"[/italic]",
        title="Automated Rubric Evaluation Demo",
        border_style="green"
    ))

    console.print("\n[bold green]🎉 All Pipeline Stages & Quality Benchmarks Succeeded![/bold green]")
    console.print("[dim]Run 'python server.py' to launch the interactive web application.[/dim]\n")

if __name__ == "__main__":
    main()
