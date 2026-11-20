# Doc-Parse Tool Plugin

Generate and edit images using Alibaba Cloud's Qwen-Image models via DashScope SDK.

## Tools

### `mineru_parse` - 文档解析

### `docling_parse` - 文档解析


## Configuration

Each tool has independent configuration fields:

| Field | Description                    | Default                  |
|-------|--------------------------------|--------------------------|
| `api_key` | Parse Server API key (required) | —                        |
| `endpoint` | Regional API endpoint          | `https://localhost:5001` |
| `timeout` | Request timeout in seconds     | 120                      |


**Endpoints:**
- MinerU: `https://opendatalab.github.io/MinerU/zh/`
- Docling: `https://docling-project.github.io/docling/usage/api_server/`

> Note: API key and endpoint must be from the same region.

Get your API key at: https://bailian.console.aliyun.com/

## Output

Generated files are saved to `{DEFAULT_MEDIA_DIR}/{user_id}/` as md and json files.
