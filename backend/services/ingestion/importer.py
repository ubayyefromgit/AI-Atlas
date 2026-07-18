# backend/services/ingestion/importer.py
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd

from repositories.company import company_repo
from repositories.problem import problem_repo
from repositories.sector import sector_repo
from repositories.mapping import mapping_repo, CreateMapping
from schemas.company import CreateCompany, UpdateCompany
from schemas.problem import ProblemBase
from schemas.sector import SectorBase
from services.ingestion.transformers import (
    transform_company_row, transform_problem_row, 
    transform_sector_row, transform_mapping_row
)
from services.ingestion.validators import (
    validate_company, validate_problem, validate_sector
)
from services.ingestion.report import ImportReport

logger = logging.getLogger("ingestion")

class DataImporter:
    def __init__(self, db: Session, report: ImportReport, dry_run: bool = False):
        self.db = db
        self.report = report
        self.dry_run = dry_run

    def import_sectors(self, df: pd.DataFrame):
        for index, row in df.iterrows():
            try:
                row_dict = transform_sector_row(row)
                sector, warnings = validate_sector(row_dict)
                
                if warnings:
                    logger.warning(f"Row {index} (Sector): {', '.join(warnings)}")
                    self.report.add_warning()
                    
                if not sector:
                    self.report.increment("sectors", "skipped")
                    continue

                existing = sector_repo.get_by_name(self.db, name=sector.name)
                
                if not self.dry_run:
                    if existing:
                        sector_repo.update(self.db, db_obj=existing, obj_in=sector)
                        self.report.increment("sectors", "updated")
                    else:
                        sector_repo.create(self.db, obj_in=sector)
                        self.report.increment("sectors", "imported")
                else:
                    self.report.increment("sectors", "imported" if not existing else "updated")

            except Exception as e:
                self.db.rollback()
                logger.error(f"Error importing sector at row {index}: {e}")
                self.report.add_error()
                self.report.increment("sectors", "skipped")

    def import_companies(self, df: pd.DataFrame):
        for index, row in df.iterrows():
            try:
                row_dict = transform_company_row(row)
                company, warnings = validate_company(row_dict)
                
                if warnings:
                    logger.warning(f"Row {index} (Company): {', '.join(warnings)}")
                    self.report.add_warning()
                    
                if not company:
                    self.report.increment("companies", "skipped")
                    continue

                existing = company_repo.get_by_name(self.db, name=company.name)
                
                if not self.dry_run:
                    if existing:
                        # Need an UpdateCompany schema instead of CreateCompany
                        update_schema = UpdateCompany(**company.model_dump(exclude_unset=True))
                        company_repo.update(self.db, db_obj=existing, obj_in=update_schema)
                        self.report.increment("companies", "updated")
                    else:
                        company_repo.create(self.db, obj_in=company)
                        self.report.increment("companies", "imported")
                else:
                    self.report.increment("companies", "imported" if not existing else "updated")

            except Exception as e:
                self.db.rollback()
                logger.error(f"Error importing company at row {index}: {e}")
                self.report.add_error()
                self.report.increment("companies", "skipped")

    def import_problems(self, df: pd.DataFrame):
        for index, row in df.iterrows():
            try:
                row_dict = transform_problem_row(row)
                problem, warnings = validate_problem(row_dict)
                
                if warnings:
                    logger.warning(f"Row {index} (Problem): {', '.join(warnings)}")
                    self.report.add_warning()
                    
                if not problem:
                    self.report.increment("problems", "skipped")
                    continue

                existing = problem_repo.get_by_category(self.db, category=problem.category)
                
                if not self.dry_run:
                    if existing:
                        problem_repo.update(self.db, db_obj=existing, obj_in=problem)
                        self.report.increment("problems", "updated")
                    else:
                        problem_repo.create(self.db, obj_in=problem)
                        self.report.increment("problems", "imported")
                else:
                    self.report.increment("problems", "imported" if not existing else "updated")

            except Exception as e:
                self.db.rollback()
                logger.error(f"Error importing problem at row {index}: {e}")
                self.report.add_error()
                self.report.increment("problems", "skipped")

    def import_mappings(self, df: pd.DataFrame):
        for index, row in df.iterrows():
            try:
                row_dict = transform_mapping_row(row)
                company_names = row_dict.get("company_names") or []
                problem_category = row_dict.get("problem_category")

                if not company_names or not problem_category:
                    logger.warning(f"Row {index} (Mapping): Missing vendors or problem_category")
                    self.report.add_warning()
                    self.report.increment("mappings", "skipped")
                    continue

                # Resolve the problem once per row
                problem = problem_repo.get_by_category(self.db, category=problem_category)
                if not problem:
                    from models.problem import Problem
                    prefix = problem_category[:20]
                    problem = self.db.query(Problem).filter(Problem.category.ilike(f"%{prefix}%")).first()

                if not problem:
                    logger.warning(f"Row {index} (Mapping): Problem '{problem_category}' not found. Auto-creating.")
                    from schemas.problem import ProblemBase
                    placeholder_problem = ProblemBase(category=problem_category)
                    problem = problem_repo.create(self.db, obj_in=placeholder_problem)
                    self.report.increment("problems", "imported")

                # Create one mapping per vendor listed in the ranked vendors column
                for company_name in company_names:
                    company = company_repo.get_by_name(self.db, name=company_name)
                    if not company:
                        from models.company import Company
                        company = self.db.query(Company).filter(
                            Company.name.ilike(f"%{company_name}%")
                        ).first()

                    if not company:
                        logger.warning(f"Row {index} (Mapping): Company '{company_name}' not found — skipping this vendor.")
                        self.report.add_warning()
                        continue

                    segment = row_dict.get("segment_name")
                    existing = mapping_repo.get_by_unique_keys(
                        self.db,
                        company_id=company.id,
                        problem_id=problem.id,
                        segment=segment
                    )

                    if not self.dry_run:
                        mapping_in = CreateMapping(
                            company_id=company.id,
                            problem_id=problem.id,
                            segment=segment,
                            roi_benchmark=row_dict.get("evidence")
                        )
                        if existing:
                            mapping_repo.update(self.db, db_obj=existing, obj_in=mapping_in)
                            self.report.increment("mappings", "updated")
                        else:
                            mapping_repo.create(self.db, obj_in=mapping_in)
                            self.report.increment("mappings", "imported")
                    else:
                        self.report.increment("mappings", "imported" if not existing else "updated")

            except Exception as e:
                self.db.rollback()
                logger.error(f"Error importing mapping at row {index}: {e}")
                self.report.add_error()
                self.report.increment("mappings", "skipped")
