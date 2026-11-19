"""PDF to Markdown converter using MinerU service."""

from __future__ import annotations

import argparse
import logging
import os
import httpx,json
import zipfile
import time
from io import BytesIO
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)

if 'MINERU_BASE_URL' not in os.environ:
    os.environ['MINERU_BASE_URL'] = 'http://8.145.35.112:8003'


class MinerUClient:
    def __init__(
        self,
        base_url: str = None,
        api_token: str = None,
        is_ocr: bool = True,
        language: str = None,
        enable_table: bool = True,
        enable_formula: bool = True,
        model_version: str | None = None,
        page_ranges: str = "1--1", # 默认第一页到最后一页
        poll_timeout_seconds: int = 300,
        poll_interval_seconds: int = 5,
    ):
        self.base_url = base_url or os.getenv("MINERU_BASE_URL", "")
        self.api_token = api_token or os.getenv("MINERU_API_TOKEN", "")
        self.is_ocr = is_ocr
        self.language = language or os.getenv("MINERU_LANGUAGE", "ch")
        self.enable_table = enable_table
        self.enable_formula = enable_formula
        self.model_version = model_version or os.getenv("MINERU_MODEL_VERSION", "pipeline")
        self.page_ranges = page_ranges
        self.poll_timeout_seconds = poll_timeout_seconds
        self.poll_interval_seconds = poll_interval_seconds
        self.headers = {"Authorization": f"Bearer {self.api_token}"}
        if not self.base_url:
            raise ValueError("MINERU_BASE_URL is not set")
        if not self.api_token:
            raise ValueError("MINERU_API_TOKEN is not set")

    def export_batch_markdown_bundle(
        self,
        file_paths: list[Path],
        output_dir: Path,
    ):
        logger.info(f"[MinerU] Starting export_batch_markdown_bundle for {len(file_paths)} files")
        output_dir.mkdir(parents=True, exist_ok=True)
        batch_id, file_urls = self.submit_tasks(file_paths)
        logger.info(f"[MinerU] Task submitted, batch_id={batch_id}")
        all_dones = self._poll_until_all_done(batch_id, file_urls)
        logger.info(f"[MinerU] Polling completed for batch_id={batch_id}")

        zip_contents = self._download_zip(all_dones)
        total_bytes = sum(len(v) for v in zip_contents.values())
        logger.info(f"[MinerU] Downloaded zip, size={total_bytes} bytes")
        self._extract_from_zip(zip_contents, output_dir)
        logger.info(f"[MinerU] Extracted to {output_dir}")
      
    def submit_tasks(self, file_paths: list[Path], timeout:float=60.0) -> tuple[str, list[str]]:
        logger.info(f"[MinerU] Submitting {len(file_paths)} files to {self.base_url}")
        payload = {
            "files": [
                {"name": fp.name, "is_ocr": self.is_ocr, "page_ranges": self.page_ranges}
                for fp in file_paths
            ],
            "enable_table": self.enable_table,
            "enable_formula": self.enable_formula,
            "language": self.language,
            "model_version": self.model_version,
        }
        with httpx.Client(base_url=self.base_url, timeout=timeout) as client:
            resp = client.post("/file-urls/batch", headers=self.headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        if data["code"] != 0:
            raise ValueError(f"MinerU create task failed: {data.get('msg', 'unknown error')}")

        task_data = data.get("data", {})
        batch_id = task_data.get("batch_id")
        file_urls = task_data.get("file_urls")

        with httpx.Client(timeout=timeout) as client:
            for fp, url in zip(file_paths, file_urls):
                with fp.open("rb") as f:
                    resp = client.put(url, content=f)
                if resp.status_code not in (200, 201):
                    logger.error(f"MinerU upload failed for {fp.name} with status {resp.status_code}")
                    raise ValueError(f"MinerU upload failed for {fp.name} with status {resp.status_code}")
        return batch_id, file_urls

    def _poll_until_all_done(self, batch_id: str, file_urls:list[str], timeout:float=6000.0) -> dict[str, str]:
        logger.info(f"[MinerU] Starting polling for batch_id={batch_id}")
        start_time = time.time()
        with httpx.Client(base_url=self.base_url, timeout=timeout) as client:
            all_dones = dict()
            while len(all_dones) < len(file_urls):
                elapsed = time.time() - start_time
                if elapsed > self.poll_timeout_seconds:
                    raise TimeoutError(f"Poll timeout after {self.poll_timeout_seconds}s for batch_id={batch_id}")
                resp = client.get(f"/extract-results/batch/{batch_id}", headers=self.headers)
                resp.raise_for_status()
                poll_data = resp.json()
                if poll_data.get("code") != 0:
                    raise ValueError(f"MinerU poll failed: {poll_data.get('msg', 'unknown error')}")
                extract_result = poll_data.get("data", {}).get("extract_result")
                for item in extract_result:
                    file_name = Path(item['file_name']).stem
                    if item['state'] == 'done':
                        all_dones[file_name] = item["full_zip_url"]
                        logger.debug(f"[MinerU] File {file_name} done")
                    elif item['state'] == 'failed':
                        all_dones[file_name] = "failed"
                        logger.error(f"MinerU parse failed for {file_name}: {item.get('err_msg')}")
                if len(all_dones) < len(file_urls):
                    logger.debug(f"[MinerU] Waiting for {len(file_urls) - len(all_dones)} files...")
                    time.sleep(self.poll_interval_seconds)
        logger.info(f"[MinerU] All {len(all_dones)} files completed")
        return all_dones

      
    def _download_zip(self, all_dones: dict[str,str], timeout:float=60.0) -> dict[str,bytes]:
        logger.info(f"[MinerU] Downloading {len(all_dones)} zip files")
        zip_contents = {}
        with httpx.Client(timeout=timeout) as client:
            for file_name, zip_url in all_dones.items():
                logger.debug(f"[MinerU] Downloading {file_name}")
                zip_resp = client.get(zip_url)
                zip_resp.raise_for_status()
                zip_contents[file_name] = zip_resp.content
                logger.debug(f"[MinerU] Downloaded {file_name}, size={len(zip_resp.content)} bytes")
        return zip_contents

    def _extract_from_zip(self, zip_contents: dict[str,bytes], extract_dir: Path) -> str:
        for file_name, zip_content in zip_contents.items():
            file_output_dir = extract_dir / file_name
            with zipfile.ZipFile(BytesIO(zip_content)) as zf:
                zf.extractall(file_output_dir)
        logger.info(f"[MinerU] Extracted {len(zip_contents)} files to {extract_dir}")


class MinerUClientLocal:
    def __init__(
        self,
        base_url: str = None,
        lang_list: list[str] = None,
        backend: str = "pipeline",
        parse_method: str = "auto",
        formula_enable: bool = True,
        table_enable: bool = True,
        return_md: bool = True,
        return_images: bool = True,
        response_format_zip: bool = True,
        return_middle_json: bool = False,
        return_content_list: bool = False,
        return_model_output: bool = False,
        start_page_id: int = 0,
        end_page_id: int | None = None,
        poll_timeout_seconds: int = 300,
        poll_interval_seconds: int = 5,
    ):
        self.base_url = base_url or os.getenv("MINERU_BASE_URL", "http://127.0.0.1:8000")
        self.poll_timeout_seconds = poll_timeout_seconds
        self.poll_interval_seconds = poll_interval_seconds
        self._form_data = {
            "lang_list": lang_list if lang_list is not None else ["ch"],
            "backend": backend,
            "parse_method": parse_method,
            "formula_enable": formula_enable,
            "table_enable": table_enable,
            "return_md": return_md,
            "response_format_zip": response_format_zip,
            "return_images": return_images,
            "return_middle_json": return_middle_json,
            "return_content_list": return_content_list,
            "return_model_output": return_model_output,
            "start_page_id": start_page_id,
            "end_page_id": end_page_id,            
        }
    
    def export_batch_markdown_bundle(
        self,
        file_paths: list[Path],
        output_dir: Path,
    ) -> dict[str, dict]:
        logger.info(f"[MinerU] Starting export_batch_markdown_bundle for {len(file_paths)} files")
        output_dir.mkdir(parents=True, exist_ok=True)
        task_id = self.submit_tasks(file_paths)
        logger.info(f"[MinerU] Task submitted, task_id={task_id}")
        result = self._poll_until_all_done(task_id)
        logger.info(f"[MinerU] Polling completed for task_id={task_id}")

        zip_content = self._download_zip(task_id)
        logger.info(f"[MinerU] Downloaded zip, size={len(zip_content)} bytes")
        self._extract_from_zip(zip_content, output_dir)
        logger.info(f"[MinerU] Extracted to {output_dir}")
        return result
    
    def dryrun_export_batch_markdown_bundle(
        self,
        file_paths: list[Path],
        output_dir: Path,
    ) -> dict[str, dict]:
        logger.info(f"[MinerU] Starting export_batch_markdown_bundle for {len(file_paths)} files")
        output_dir.mkdir(parents=True, exist_ok=True)
        task_id = 'self.submit_tasks(file_paths)'
        logger.info(f"[MinerU] Task submitted, task_id={task_id}")
        result = dict(task_id=task_id,file_paths=str(file_paths))
        logger.info(f"[MinerU] Polling completed for task_id={task_id}")
        
        logger.info(f"[MinerU] Extracted to {output_dir}")
        return result
        
    def submit_tasks(self, file_paths: list[Path], timeout:float=600.0) -> str:
        with httpx.Client(base_url=self.base_url, timeout=timeout) as client:
            files = [
                ("files", (fp.name, fp.open("rb"), "application/pdf"))
                for fp in file_paths]
            resp = client.post("/tasks", data=self._form_data, files=files)
            resp.raise_for_status()
            task_id = resp.json().get("task_id")
        return task_id

    def _poll_until_all_done(self, task_id: str, timeout:float=6000.0) -> dict[str, dict]:
        with httpx.Client(base_url=self.base_url, timeout=timeout) as client:
            resp = client.get(f"tasks/{task_id}")
            json = resp.json()
            while json['status']!='completed':
                if json['status'] == 'failed':
                    logger.error(f"[MinerU] Task failed, task_id={task_id}, error={json['error']}")
                    break
                time.sleep(self.poll_interval_seconds)
                resp = client.get(f"tasks/{task_id}")
                json = resp.json()
            resp.raise_for_status()
            return json
        return None

    def _download_zip(self, task_id: str, timeout:float=60.0) -> bytes:
        with httpx.Client(base_url=self.base_url, timeout=timeout) as client:
            resp = client.get(
                f"/tasks/{task_id}/result",
                params={"response_format_zip": "true"},
            )
            resp.raise_for_status()
            return resp.content

    def _extract_from_zip(self, zip_content: bytes, extract_dir: Path) -> dict:
        with zipfile.ZipFile(BytesIO(zip_content)) as zf:
            zf.extractall(extract_dir)

def chunk_files(files, chunk_size=10):
    """将 files 列表切分成多个子列表，每个最多 chunk_size 个"""
    return [files[i:i + chunk_size] for i in range(0, len(files), chunk_size)]

def get_subdirectories(root_path: Path) -> List[Path]:
    """获取所有子目录（包括根目录）"""
    subdirs = []
    for item in root_path.rglob('*'):
        if item.is_dir():
            subdirs.append(item)
    # 按路径深度排序，确保先处理深层目录
    subdirs.sort(key=lambda p: len(p.parts), reverse=True)
    if not subdirs:
        subdirs.append(root_path)
    return subdirs

def parse_single_directory(dir_path: Path, download_dir: Path,
                          file_extensions: List[str] = None, **kwargs) -> Dict[str, Any]:
    """
    解析单个目录下的文件
    """
    # 获取该目录下的所有文件
    if file_extensions is None:
        # 默认支持常见文档格式
        file_extensions = ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx']
    
    files = []
    for ext in file_extensions:
        files.extend(dir_path.glob(f'*{ext}'))
    
    # 过滤掉目录，只保留文件
    files = [f for f in files if f.is_file()]
    
    if not files:
        return {
            "ok": True,
            "result": [],
            "error": None,
            "directory": str(dir_path)
        }
    
    # 为当前目录创建独立的MinerUClientLocal实例
    # 每个实例使用不同的端口或标识
    mineru = MinerUClientLocal()
    
    try:
        # 为每个子目录创建独立的下载目录
        sub_download_dir = download_dir / dir_path.relative_to(dir_path.parent)
        sub_download_dir.mkdir(parents=True, exist_ok=True)
        
        #chunks = chunk_files(files)
        responses = []
        for subfile in files:
            output_loc: Path = sub_download_dir/ subfile.name.replace('.pdf','') /'auto'
            if output_loc.exists():
                logger.info(f'file {str(subfile)} already parsed!')
                continue
            resp = mineru.export_batch_markdown_bundle(
                [subfile], 
                sub_download_dir.resolve()
            )
            responses.append(resp)
        
        return {
            "ok": True,
            "result": responses,
            "error": None,
            "directory": str(dir_path),
            "file_count": len(files)
        }
    except Exception as e:
        logger.error(f"解析目录 {dir_path} 出错: {e}")
        return {
            "ok": False,
            "result": None,
            "error": str(e),
            "directory": str(dir_path)
        }

def batch_parse_document(file_path: str, 
                         download_dir: str,
                         file_extensions: List[str] = None,                     
                         **kwargs) -> Dict[str, Any]:
    """
    批量解析文档，支持多级目录
    
    Args:
        file_path: 根目录路径
        download_dir: 下载目录        
        file_extensions: 支持的文件扩展名列表        
        **kwargs: 其他参数
    
    Returns:
        包含所有解析结果的字典
    """
    root_path = Path(file_path)
    download_root = Path(download_dir)
    
    if not root_path.exists():
        return {
            "ok": False,
            "error": f"路径不存在: {file_path}",
            "result": None
        }
    
    # 获取所有子目录
    subdirs = get_subdirectories(root_path)
    
    if not subdirs:
        return {
            "ok": False,
            "error": "没有找到任何子目录",
            "result": None
        }
    
    logger.info(f"找到 {len(subdirs)} 个目录需要处理")
    
    # 存储所有结果
    all_results = []
    errors = []
    success_count = 0
    

    # 每个子目录使用独立的MinerUClientLocal实例
    for dir_path in subdirs:
        resp = parse_single_directory(dir_path,download_root,file_extensions)
        if resp['ok']:
            all_results.append(resp['result'])
        else:
            errors.append(resp['error'])

    # 汇总结果
    return {
        "ok": len(errors) == 0,
        "result": all_results,
        "error": None if len(errors) == 0 else f"有 {len(errors)} 个目录处理失败",
        "summary": {
            "total_directories": len(subdirs),
            "success_directories": success_count,
            "failed_directories": len(errors),
            "errors": errors if errors else None
        }
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run MinerU in hosted API mode or local open-source CLI mode.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  python scripts/mineru_parsers.py --file-path "C:/docs/paper.pdf" --download-dir "C:/docs/mk"


API environment:
  MINERU_API_TOKEN                 Required for --mode api
  MINERU_API_BASE_URL             Optional, default: https://mineru.net
  MINERU_API_TIMEOUT              Optional, default: 60
  MINERU_API_POLL_TIMEOUT         Optional, default: 900
  MINERU_API_POLL_INTERVAL        Optional, default: 5

""",
    )

    input_group = parser.add_mutually_exclusive_group(required=True)    
    input_group.add_argument("--file-path", help="Local document path")
    
    parser.add_argument(
        "--language",
        default="auto",
        help="Language hint for MinerU API or local CLI (default: auto)",
    )
    parser.add_argument(
        "--ocr",
        action="store_true",
        help="Force OCR mode",
    )
    parser.add_argument(
        "--disable-formula",
        action="store_true",
        help="Disable formula extraction",
    )
    parser.add_argument(
        "--no-wait",
        action="store_true",
        help="Return after task submission without polling; API mode only",
    )
    parser.add_argument(
        "--no-download",
        action="store_true",
        help="Skip downloading full_zip_url after API completion; API mode only",
    )
    parser.add_argument(
        "--download-dir",
        help="Custom directory for API downloads or local MinerU output files",
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")

    args = parser.parse_args()

    result = batch_parse_document(        
        file_path=args.file_path,
        download_dir=args.download_dir,    
        language=args.language,
        enable_formula=not args.disable_formula,
        ocr=args.ocr,
        wait=not args.no_wait,
        download=not args.no_download            
    )

    json_output = json.dumps(
        result,
        indent=2 if args.pretty else None,
        ensure_ascii=False,
    )

    if json_output:
        print(json_output)

    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

