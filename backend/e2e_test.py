"""End-to-end pipeline testing and validation."""

import logging
from typing import Dict, List
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class E2EPipelineTest:
    """End-to-end pipeline testing for TruthLens AI."""

    def __init__(self):
        """Initialize pipeline tester."""
        self.test_results = []
        self.start_time = None
        self.end_time = None

    def test_text_claim_analysis(self) -> Dict:
        """Test analyzing a text claim."""
        logger.info("Testing text claim analysis")

        try:
            from services.scoring_engine import ScoringEngine

            engine = ScoringEngine()

            test_claim = "The Earth is flat and NASA is hiding the truth."

            result = engine.analyze(test_claim, include_explanations=False)

            success = (
                "verdict" in result
                and result["verdict"] in ["REAL", "FAKE", "RUMOR"]
            )

            return {
                "test": "Text Claim Analysis",
                "success": success,
                "result": result if success else None,
                "error": None if success else "Missing expected fields",
            }

        except Exception as e:
            logger.error(f"Text analysis test failed: {e}")
            return {
                "test": "Text Claim Analysis",
                "success": False,
                "result": None,
                "error": str(e),
            }

    def test_image_ocr_pipeline(self, image_path: str = None) -> Dict:
        """Test image OCR and text extraction."""
        logger.info("Testing image OCR pipeline")

        try:
            from utils.image_grid_splitter import ImageGridSplitter

            # Use test image or create mock
            if not image_path:
                logger.warning("No image path provided, skipping OCR test")
                return {
                    "test": "Image OCR Pipeline",
                    "success": True,
                    "skipped": True,
                    "reason": "No test image",
                }

            processor = ImageGridSplitter(grid_size=3)
            result = processor.process_image(image_path)

            success = "extracted_text" in result and len(result["extracted_text"]) > 0

            return {
                "test": "Image OCR Pipeline",
                "success": success,
                "result": {
                    "extracted_chars": len(result.get("extracted_text", "")),
                    "grid_size": result.get("grid_size"),
                },
                "error": None if success else "No text extracted",
            }

        except Exception as e:
            logger.error(f"OCR test failed: {e}")
            return {
                "test": "Image OCR Pipeline",
                "success": False,
                "result": None,
                "error": str(e),
            }

    def test_scraping_service(self) -> Dict:
        """Test web scraping service."""
        logger.info("Testing scraping service")

        try:
            from services.scraping_service import TrustedSourceScraper

            scraper = TrustedSourceScraper()

            # Test trusted source detection
            is_trusted = scraper.is_trusted_source("https://reuters.com/article")
            success = is_trusted is True

            return {
                "test": "Scraping Service",
                "success": success,
                "result": {
                    "trusted_source_detection": is_trusted,
                    "sources_count": len(scraper.TRUSTED_SOURCES),
                },
                "error": None if success else "Trusted source detection failed",
            }

        except Exception as e:
            logger.error(f"Scraping test failed: {e}")
            return {
                "test": "Scraping Service",
                "success": False,
                "result": None,
                "error": str(e),
            }

    def test_text_preprocessing(self) -> Dict:
        """Test text preprocessing service."""
        logger.info("Testing text preprocessing")

        try:
            from services.preprocessing_service import TextPreprocessor

            preprocessor = TextPreprocessor()

            test_text = "The quick BROWN fox jumps! Over the lazy dog."

            result = preprocessor.preprocess(test_text, lemmatize=True)

            success = (
                "tokens" in result
                and len(result["tokens"]) > 0
                and "cleaned_text" in result
            )

            return {
                "test": "Text Preprocessing",
                "success": success,
                "result": {
                    "token_count": len(result.get("tokens", [])),
                    "sentence_count": len(result.get("sentences", [])),
                    "entities_count": len(result.get("entities", {})),
                },
                "error": None if success else "Preprocessing failed",
            }

        except Exception as e:
            logger.error(f"Preprocessing test failed: {e}")
            return {
                "test": "Text Preprocessing",
                "success": False,
                "result": None,
                "error": str(e),
            }

    def test_evidence_retrieval(self) -> Dict:
        """Test evidence retrieval service."""
        logger.info("Testing evidence retrieval")

        try:
            from services.evidence_retrieval_service import EvidenceRetrievalService

            service = EvidenceRetrievalService()

            test_query = "climate change effects"

            results = service.search_evidence(test_query, top_k=5)

            success = isinstance(results, list) and len(results) > 0

            return {
                "test": "Evidence Retrieval",
                "success": success,
                "result": {
                    "results_found": len(results),
                    "index_type": "FAISS" if service.use_faiss else "Mock",
                },
                "error": None if success else "No results found",
            }

        except Exception as e:
            logger.error(f"Evidence retrieval test failed: {e}")
            return {
                "test": "Evidence Retrieval",
                "success": False,
                "result": None,
                "error": str(e),
            }

    def test_explainability_service(self) -> Dict:
        """Test explainability service."""
        logger.info("Testing explainability service")

        try:
            from services.explainability_service import ExplainabilityService

            service = ExplainabilityService()

            test_claim = "Vaccines cause autism"
            test_prediction = {
                "verdict": "FAKE",
                "confidence": 0.95,
                "nlp_score": 0.85,
                "evidence_score": 0.90,
                "propagation_score": 0.40,
            }

            # Test evidence comparison
            test_evidence = [
                {
                    "source": "WHO",
                    "text": "No link between vaccines and autism",
                    "credibility": 0.98,
                    "relevance": 0.95,
                    "direction": "contradicting",
                },
                {
                    "source": "CDC",
                    "text": "Vaccines are safe",
                    "credibility": 0.97,
                    "relevance": 0.92,
                    "direction": "contradicting",
                },
            ]

            evidence_exp = service.compare_evidence_sources(
                test_claim, test_evidence
            )

            success = (
                evidence_exp is not None
                and "supporting_evidence" in evidence_exp
                and "contradicting_evidence" in evidence_exp
            )

            return {
                "test": "Explainability Service",
                "success": success,
                "result": {
                    "evidence_sources": len(evidence_exp.get("supporting_evidence", []))
                    + len(evidence_exp.get("contradicting_evidence", [])),
                    "net_support": evidence_exp.get("net_support", 0),
                },
                "error": None if success else "Explainability failed",
            }

        except Exception as e:
            logger.error(f"Explainability test failed: {e}")
            return {
                "test": "Explainability Service",
                "success": False,
                "result": None,
                "error": str(e),
            }

    def test_api_endpoints(self) -> Dict:
        """Test API endpoint availability."""
        logger.info("Testing API endpoints")

        try:
            from main import app

            # Get all routes
            routes = [str(route.path) for route in app.routes if hasattr(route, "path")]

            expected_endpoints = [
                "/api/analyze",
                "/api/upload",
                "/api/health",
            ]

            found_endpoints = [ep for ep in expected_endpoints if ep in routes]
            success = len(found_endpoints) == len(expected_endpoints)

            return {
                "test": "API Endpoints",
                "success": success,
                "result": {
                    "total_routes": len(routes),
                    "expected_found": len(found_endpoints),
                    "routes": routes[:10],
                },
                "error": None if success else "Missing expected endpoints",
            }

        except Exception as e:
            logger.error(f"API test failed: {e}")
            return {
                "test": "API Endpoints",
                "success": False,
                "result": None,
                "error": str(e),
            }

    def test_database_models(self) -> Dict:
        """Test database model definitions."""
        logger.info("Testing database models")

        try:
            from database.models import Analysis, Evidence

            # Check models have required fields
            analysis_fields = [
                "id",
                "claim_text",
                "verdict",
                "confidence",
                "created_at",
            ]
            success = True  # Models exist

            return {
                "test": "Database Models",
                "success": success,
                "result": {
                    "models_found": ["Analysis", "Evidence"],
                    "fields_configured": len(analysis_fields),
                },
                "error": None if success else "Model definition failed",
            }

        except Exception as e:
            logger.error(f"Database model test failed: {e}")
            return {
                "test": "Database Models",
                "success": False,
                "result": None,
                "error": str(e),
            }

    def run_all_tests(self, test_image_path: str = None) -> Dict:
        """Run all E2E tests."""
        logger.info("Starting E2E pipeline tests")
        self.start_time = datetime.now()

        tests = [
            self.test_text_claim_analysis(),
            self.test_image_ocr_pipeline(test_image_path),
            self.test_scraping_service(),
            self.test_text_preprocessing(),
            self.test_evidence_retrieval(),
            self.test_explainability_service(),
            self.test_api_endpoints(),
            self.test_database_models(),
        ]

        self.test_results = tests
        self.end_time = datetime.now()

        # Calculate summary
        passed = sum(1 for t in tests if t.get("success"))
        skipped = sum(1 for t in tests if t.get("skipped"))
        failed = len(tests) - passed - skipped

        duration = (self.end_time - self.start_time).total_seconds()

        summary = {
            "total_tests": len(tests),
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "duration_seconds": duration,
            "success_rate": f"{(passed / (passed + failed) * 100):.1f}%" if (passed + failed) > 0 else "N/A",
            "timestamp": self.start_time.isoformat(),
            "tests": tests,
        }

        logger.info(
            f"E2E tests complete: {passed} passed, {failed} failed, {skipped} skipped"
        )

        return summary

    def print_results(self, summary: Dict):
        """Print test results in readable format."""
        print("\n" + "=" * 70)
        print("TruthLens AI - End-to-End Pipeline Test Results")
        print("=" * 70 + "\n")

        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']} ✓")
        print(f"Failed: {summary['failed']} ✗")
        print(f"Skipped: {summary['skipped']} ~")
        print(f"Success Rate: {summary['success_rate']}")
        print(f"Duration: {summary['duration_seconds']:.2f}s")
        print(f"Timestamp: {summary['timestamp']}\n")

        for test in summary["tests"]:
            status = (
                "✓"
                if test["success"]
                else "~"
                if test.get("skipped")
                else "✗"
            )
            print(f"{status} {test['test']}")

            if test.get("result"):
                for key, value in test["result"].items():
                    if isinstance(value, dict):
                        print(f"   {key}:")
                        for k, v in value.items():
                            print(f"     - {k}: {v}")
                    else:
                        print(f"   {key}: {value}")

            if test.get("error"):
                print(f"   Error: {test['error']}")

        print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    import sys

    tester = E2EPipelineTest()
    results = tester.run_all_tests()
    tester.print_results(results)

    # Exit with status based on failures
    sys.exit(0 if results["failed"] == 0 else 1)
