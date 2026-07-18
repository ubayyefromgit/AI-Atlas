"""
Smart Problem-Company Mapping Backfill
Infers problem → company relationships from text similarity:
- company.ai_category vs problem.ai_solution_use_case
- company.use_cases vs problem.category
- company.segment_tags vs problem keywords
"""
import sys, os
sys.path.insert(0, 'backend')

from core.database import SessionLocal
from models.company import Company
from models.problem import Problem
from models.mapping import ProblemCompanyMapping

def normalize(text: str) -> set:
    if not text:
        return set()
    import re
    words = re.sub(r'[^a-z0-9\s]', ' ', text.lower()).split()
    # Remove stopwords
    stop = {'the', 'a', 'an', 'and', 'or', 'for', 'in', 'of', 'to', 'with', 'by', 'on', 'at', 'is', 'are', 'was'}
    return {w for w in words if w not in stop and len(w) > 2}

def score_company_problem(company, problem) -> float:
    """Score how well a company matches a problem (0.0 to 1.0)"""
    score = 0.0
    
    # Collect company text tokens
    company_tokens = set()
    for field in [company.ai_category, company.germany_presence, company.deployment_evidence]:
        company_tokens |= normalize(field)
    for lst in [company.use_cases or [], company.segment_tags or []]:
        for item in lst:
            company_tokens |= normalize(item)
    
    # Collect problem text tokens
    problem_tokens = normalize(problem.category)
    problem_tokens |= normalize(problem.ai_solution_use_case)
    
    if not company_tokens or not problem_tokens:
        return 0.0
    
    # Jaccard-like overlap
    intersection = company_tokens & problem_tokens
    if not intersection:
        return 0.0
    
    score = len(intersection) / min(len(company_tokens), len(problem_tokens))
    return score


def main():
    db = SessionLocal()
    
    companies = db.query(Company).filter(Company.is_deleted == False).all()
    problems = db.query(Problem).all()
    existing_mappings = {(m.company_id, m.problem_id) for m in db.query(ProblemCompanyMapping).all()}
    
    print(f"Companies: {len(companies)}, Problems: {len(problems)}, Existing mappings: {len(existing_mappings)}")
    
    THRESHOLD = 0.12  # Minimum score to create a mapping
    new_mappings = 0
    
    for company in companies:
        for problem in problems:
            if (company.id, problem.id) in existing_mappings:
                continue  # Skip already mapped
            
            score = score_company_problem(company, problem)
            if score >= THRESHOLD:
                mapping = ProblemCompanyMapping(
                    company_id=company.id,
                    problem_id=problem.id,
                    roi_benchmark=f"Inferred from company profile (confidence: {score:.2f})"
                )
                db.add(mapping)
                existing_mappings.add((company.id, problem.id))
                new_mappings += 1
    
    db.commit()
    
    total = db.query(ProblemCompanyMapping).count()
    print(f"Added {new_mappings} new mappings. Total mappings now: {total}")
    
    # Show distribution
    from sqlalchemy import func
    counts = db.query(ProblemCompanyMapping.company_id, func.count(ProblemCompanyMapping.id))\
        .group_by(ProblemCompanyMapping.company_id).all()
    companies_with_mappings = len(counts)
    print(f"Companies with at least 1 problem: {companies_with_mappings} / {len(companies)}")
    
    db.close()

if __name__ == '__main__':
    main()
