from __future__ import annotations

import csv
import logging
import uuid
from pathlib import Path

from app.rag.schemas import KnowledgeDocument

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".pdf", ".md", ".markdown", ".txt", ".csv"}


class LoadedDocument:
    """A document plus its raw pages of text, ready for chunking."""

    def __init__(
        self,
        document: KnowledgeDocument,
        pages: list[tuple[int | None, str]],
    ):
        self.document = document
        self.pages = pages


class DocumentLoader:
    """Loads knowledge documents (PDF, Markdown, TXT, CSV) from disk.

    Args:
        knowledge_dir: Directory to recursively scan for supported files.
    """

    def __init__(self, knowledge_dir: str | Path):
        self.knowledge_dir = Path(knowledge_dir)

    def discover(self) -> list[Path]:
        """Return every supported file under the knowledge directory."""

        if not self.knowledge_dir.exists():
            return []

        return sorted(
            path
            for path in self.knowledge_dir.rglob("*")
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
        )

    def load_all(self) -> list[LoadedDocument]:
        """Load every discovered document."""

        loaded: list[LoadedDocument] = []
        for path in self.discover():
            try:
                loaded.append(self.load(path))
            except Exception as exc:
                logger.warning(
                    "rag_document_load_failed path=%s error=%s",
                    path,
                    exc.__class__.__name__,
                )
        return loaded

    def load(self, path: Path) -> LoadedDocument:
        """Load a single document, returning its raw text per page."""

        suffix = path.suffix.lower()

        if suffix == ".pdf":
            pages = self._load_pdf(path)
        elif suffix == ".csv":
            pages = self._load_csv(path)
        else:
            pages = self._load_text(path)

        document = KnowledgeDocument(
            document_id=str(
                uuid.uuid5(uuid.NAMESPACE_URL, str(path.resolve()))
            ),
            document_name=path.name,
            source_path=str(path),
            file_type=suffix.lstrip("."),
        )

        return LoadedDocument(document=document, pages=pages)

    def _load_text(self, path: Path) -> list[tuple[int | None, str]]:
        text = path.read_text(encoding="utf-8", errors="ignore")
        return [(None, text)]

    def _load_csv(self, path: Path) -> list[tuple[int | None, str]]:
        rows: list[str] = []

        with path.open(newline="", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            header = next(reader, None)

            for row in reader:
                if header:
                    rows.append(
                        ", ".join(
                            f"{name}: {value}"
                            for name, value in zip(header, row)
                        )
                    )
                else:
                    rows.append(", ".join(row))

        return [(None, "\n".join(rows))]

    def _load_pdf(self, path: Path) -> list[tuple[int | None, str]]:
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError(
                "pypdf is required to ingest PDF knowledge documents. "
                "Install it with `uv add pypdf`."
            ) from exc

        reader = PdfReader(str(path))
        pages: list[tuple[int | None, str]] = []

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                pages.append((page_number, text))

        return pages
